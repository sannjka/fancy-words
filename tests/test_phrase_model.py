import unittest
from sqlalchemy.exc import IntegrityError
from app import create_app, db
from app.models import User, Phrase


class PhraseModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_phrase_representation(self):
        u = User(password='cat')
        p = Phrase(body='inextricably intertwined',
                   translation='неразрывно связанный',
                   author=u)
        self.assertEqual(
            str(p),
            "Phrase('inextricably intertwined', 'неразрывно связанный')")

    def test_phrase_author(self):
        u = User(password='cat')
        p = Phrase(body='inextricably intertwined',
                   translation='неразрывно связанный',
                   author=u)
        db.session.add(u)
        db.session.add(p)
        db.session.commit()
        phr = Phrase.query.filter_by(body='inextricably intertwined').first()
        self.assertTrue(phr.author == u)

    def test_users_phrases(self):
        u = User(password='cat')
        p1 = Phrase(body='inextricably intertwined',
                   translation='неразрывно связанный',
                   author=u)
        p2 = Phrase(body='jump the gun',
                    translation='опережать события',
                    author=u)
        db.session.add(u)
        db.session.add(p1)
        db.session.add(p2)
        db.session.commit()
        self.assertTrue(len(u.phrases.all()) == 2)

    def test_unowned_phrase(self):
        p = Phrase(body='jump the gun', translation='опережать события')
        db.session.add(p)
        with self.assertRaises(IntegrityError):
            db.session.commit()
