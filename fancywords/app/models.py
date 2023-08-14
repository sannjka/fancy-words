import reprlib
from datetime import datetime
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    avatar_file = db.Column(db.String(20), default='default.jpg',
                            nullable=False)
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
