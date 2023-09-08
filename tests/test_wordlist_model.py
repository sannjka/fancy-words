import unittest
from sqlalchemy.exc import IntegrityError
from app import create_app, db
from app.models import User, Phrase, WordList


class WorkListModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_wordlist_representation(self):
        u = User(password='cat')
        wl = WordList(title='First list', author=u)
        self.assertEqual(str(wl), "WordList('First list')")

    def test_wordlist_author(self):
        u = User(password='cat')
        wl = WordList(title='First list', author=u)
        db.session.add(u)
        db.session.add(wl)
        db.session.commit()
        wl_ = WordList.query.filter_by(title='First list').first()
        self.assertTrue(wl_.author == u)

    def test_users_wordlists(self):
        u = User(password='cat')
        wl1 = WordList(title='First list', author=u)
        wl2 = WordList(title='Second list', author=u)
        db.session.add(u)
        db.session.add(wl1)
        db.session.add(wl2)
        db.session.commit()
        self.assertTrue(len(u.authorlists.all()) == 2)

    def test_unowned_wordlist(self):
        wl = WordList(title='Firls list')
        db.session.add(wl)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_wordlist_composition(self):
        u = User(password='cat')
        wl = WordList(title='First list', author=u)
        p1 = Phrase(body='inextricably intertwined',
                    translation='неразрывно связанный',
                    author=u)
        p2 = Phrase(body='jump the gun',
            translation='опережать события',
            author=u)
        wl.add_phrase(p1)
        wl.add_phrase(p2)
        self.assertEqual(len(wl.phrases.all()), 2)

    def test_phrase_presence_in_wordlist(self):
        u = User(password='cat')
        wl1 = WordList(title='First list', author=u)
        wl2 = WordList(title='Second list', author=u)
        p = Phrase(body='inextricably intertwined',
                    translation='неразрывно связанный',
                    author=u)
        wl1.add_phrase(p)
        wl2.add_phrase(p)
        self.assertEqual(len(p.wordlists.all()), 2)

    def test_wordlist_subscription(self):
        u1 = User(password='cat')
        u2 = User(password='cat')
        wl1 = WordList(title='First list', author=u1)
        wl2 = WordList(title='Second list', author=u1)
        wl1.subscribe(u1)
        wl2.subscribe(u1)
        wl1.subscribe(u2)
        wl2.subscribe(u2)
        self.assertEqual(u1.wordlists.all(), [wl1, wl2])
        self.assertEqual(wl1.users.all(), [u1, u2])

