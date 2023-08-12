import unittest
from app import create_app, db
from app.models import User


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_representation(self):
        u = User(username='Shrek',
                 email='shrek@example.com',
                 password ='cat')
        self.assertEqual(str(u), "User('Shrek', 'shrek@example.com')")

    def test_password_setter(self):
        u = User(password='cat')
        self.assertIsNotNone(u.password_hash)

    def test_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertNotEqual(u.password_hash, u2.password_hash)

    def test_avatar_file_is_not_empty(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        self.assertIsNotNone(u.avatar_file)

    def test_member_since_is_set(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        self.assertIsNotNone(u.member_since)
