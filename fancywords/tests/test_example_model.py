import unittest
import reprlib
from sqlalchemy.exc import IntegrityError
from app import create_app, db
from app.models import Phrase, Example, User


class ExampleModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_example_representation(self):
        e = Example(body="You don't know that yet, so don't you jump the gun.")
        self.assertEqual(str(e), f"Example({reprlib.repr(e.body)})")

    def test_example_phrases(self):
        u = User(password='cat')
        p1 = Phrase(body='vicariously', author=u)
        p2 = Phrase(body='through', author=u)
        e = Example(body='I live vicariously through my students')
        p1.add_example(e)
        p2.add_example(e)
        self.assertEqual(len(e.phrases.all()), 2)

    def test_phrase_examples(self):
        u = User(password='cat')
        p = Phrase(body='vicariously', author=u)
        e1 = Example(body='I live vicariously through my students')
        e2 = Example(body='She enjoyed the wedding vicariously')
        p.add_example(e1)
        p.add_example(e2)
        self.assertEqual(len(p.examples.all()), 2)
