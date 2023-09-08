import unittest
from app import create_app, db
from app.models import User, Phrase


class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)
        # creating some data for tests
        u = User(password='cat')
        p = Phrase(body='inextricably intertwined',
                   translation='неразрывно связанный',
                   author=u)
        db.session.add(u)
        db.session.add(p)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Arbitrarily' in response.get_data(as_text=True))
        self.assertTrue('inextricably intertwined' in response.get_data(
            as_text=True))

    def test_search(self):
        # search field on navigation bar
        response = self.client.post('/', data={
            'search_field': 'inextricably'
        })
        self.assertEqual(response.status_code, 302)

        # result on home page
        response = self.client.post('/', data={
            'search_field': 'inextricably'
        }, follow_redirects=True)
        self.assertFalse('Arbitrarily' in response.get_data(
            as_text=True))
        self.assertTrue('inextricably intertwined' in response.get_data(
            as_text=True))

    def test_search_not_found(self):
        # result on home page
        response = self.client.post('/', data={
            'search_field': 'reciprocally'
        }, follow_redirects=True)
        self.assertTrue('Nothing found' in response.get_data(
            as_text=True))

    def test_search_empty(self):
        # search field on navigation bar
        response = self.client.post('/phrase/inextricably', data={
            'search_field': ''
        })
        self.assertEqual(response.status_code, 302)

        # result on home page
        response = self.client.post('/phrase/inextricably', data={
            'search_field': ''
        }, follow_redirects=True)
        self.assertTrue('Arbitrarily' in response.get_data(
            as_text=True))
        self.assertTrue('inextricably intertwined' in response.get_data(
            as_text=True))
