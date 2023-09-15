import reprlib
from datetime import datetime
from flask import current_app, url_for
from itsdangerous import URLSafeTimedSerializer as Serializer
from sqlalchemy.sql import func
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    avatar_file = db.Column(db.String(20), default='default.jpg',
                            nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    phrases = db.relationship('Phrase', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    authorlists = db.relationship('WordList', backref='author', lazy='dynamic')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'confirm': self.id})

    @staticmethod
    def get_user_by_token(token, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expiration)
        except:
            return None
        return User.query.get(data['confirm'])

    def confirm(self, token, expiration=3600):
        if self.get_user_by_token(token, expiration) != self:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

phrase_wordlist_registrations = db.Table('phrase_wordlist_registrations',
    db.Column('phrase_id', db.Integer, db.ForeignKey('phrases.id')),
    db.Column('wordlist_id', db.Integer, db.ForeignKey('wordlists.id'))
)

phrase_example_registrations = db.Table('phrase_example_registrations',
    db.Column('phrase_id', db.Integer, db.ForeignKey('phrases.id')),
    db.Column('example_id', db.Integer, db.ForeignKey('examples.id'))
)

class Phrase(db.Model):
    __tablename__ = 'phrases'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(200), index=True)
    image_file = db.Column(db.String(20), default='default.jpg')
    transcription = db.Column(db.String(200))
    meaning = db.Column(db.Text)
    translation = db.Column(db.Text, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                          nullable=False)
    wordlists = db.relationship('WordList',
                                secondary=phrase_wordlist_registrations,
                                backref=db.backref('phrases', lazy='dynamic'),
                                lazy='dynamic')
    comments = db.relationship('Comment', backref='phrase', lazy='dynamic')
    examples = db.relationship('Example',
                                secondary=phrase_example_registrations,
                                backref=db.backref('phrases', lazy='dynamic'),
                                lazy='dynamic')

    def __repr__(self):
        return f"Phrase('{self.body}', '{self.translation}')"

    def add_example(self, example):
        self.examples.append(example)
        db.session.commit()

    @classmethod
    def randome_phrase(cls):
        return cls.query.order_by(func.random()).first()

    @classmethod
    def find_phrase(cls, word):
        pattern = word.strip().lower()
        return cls.query.filter(Phrase.body.like('%' + pattern + '%')).all()

wordlist_subscriptions = db.Table('wordlist_subscriptions',
    db.Column('wordlist_id', db.Integer, db.ForeignKey('wordlists.id')),
    db.Column('user_is', db.Integer, db.ForeignKey('users.id'))
)

class WordList(db.Model):
    __tablename__ = 'wordlists'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), unique=True, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                          nullable=False)
    users = db.relationship('User',
                            secondary=wordlist_subscriptions,
                            backref=db.backref('wordlists', lazy='dynamic'),
                            lazy='dynamic')

    def __repr__(self):
        return f"WordList('{self.title}')"

    def add_phrase(self, word):
        self.phrases.append(word)
        db.session.commit()

    def remove_phrase(self, word):
        if word in self.phrases.all():
            self.phrases.remove(word)
            db.session.commit()

    def subscribe(self, user):
        self.users.append(user)
        db.session.commit()

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                          nullable=False)
    phrase_id = db.Column(db.Integer, db.ForeignKey('phrases.id'),
                          nullable=False)

    def __repr__(self):
        return f"Comment({reprlib.repr(self.body)})"


class Example(db.Model):
    __tablename__ = 'examples'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    source = db.Column(db.String(200))

    def __repr__(self):
        return f"Example({reprlib.repr(self.body)})"

    @classmethod
    def get_relevant_examples(cls, phrase):
        all_relevant = cls.query.filter(
            cls.body.like('%' + phrase.body + '%')
        ).all()
        already_linked = phrase.examples.all()
        return set(all_relevant) - set(already_linked)

    def get_phrases_found_in_example(self):
        body = self.body.replace("'", "''")
        textual_sql = text(
            "SELECT * FROM phrases "
            rf"WHERE '{body}' LIKE '%' || body || '%'"
        )
        return set(Phrase.query.from_statement(textual_sql).all())

    def get_presentation(self):
        presentation = self.body
        for phrase in  self.get_phrases_found_in_example():
            url = url_for('main.phrase_map', phrase_id=phrase.id)
            replacement = f'<a href="{url}">{phrase.body}</a>'
            presentation = presentation.replace(phrase.body, replacement)
        return presentation
