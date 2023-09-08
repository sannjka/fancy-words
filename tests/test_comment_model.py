import reprlib
import unittest
from sqlalchemy.exc import IntegrityError
from app import create_app, db
from app.models import User, Phrase, Comment


class CommentModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_comment_representation(self):
        u = User(password='cat')
        p = Phrase(body='inextricably intertwined',
                   translation='неразрывно связанный',
                   author=u)
        c = Comment(body='I had a hard time trying to memorize this phrase',
                    phrase=p,
                    author=u)
        self.assertEqual(str(c), f"Comment({reprlib.repr(c.body)})")

    def test_comment_author(self):
        u = User(password='cat')
        p = Phrase(body='inextricably intertwined',
                   translation='неразрывно связанный',
                   author=u)
        c = Comment(body='I had a hard time trying to memorize this phrase',
                    phrase=p,
                    author=u)
        db.session.add(u)
        db.session.add(p)
        db.session.add(c)
        db.session.commit()
        phr = Comment.query.filter_by(phrase=p).first()
        self.assertTrue(phr.author == u)

    def test_phrase_comments(self):
        u = User(password='cat')
        p = Phrase(body='inextricably intertwined',
                   translation='неразрывно связанный',
                   author=u)
        c1 = Comment(body='I had a hard time trying to memorize this phrase',
                    phrase=p,
                    author=u)
        c2 = Comment(body='Complicated', phrase=p, author=u)
        db.session.add(u)
        db.session.add(p)
        db.session.add(c1)
        db.session.add(c2)
        db.session.commit()
        self.assertTrue(len(p.comments.all()) == 2)
        self.assertEqual(len(u.comments.all()), 2)

    def test_unowned_comment(self):
        c = Comment(body='I had a hard time trying to memorize this phrase')
        db.session.add(c)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_comment_timestamp_is_set(self):
        u = User(password='cat')
        p = Phrase(body='inextricably intertwined',
                   translation='неразрывно связанный',
                   author=u)
        c = Comment(body='Complicated', phrase=p, author=u)
        db.session.add(u)
        db.session.add(p)
        db.session.add(c)
        db.session.commit()
        self.assertIsNotNone(c.timestamp)
