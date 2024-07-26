import unittest
from flask import url_for
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
        self.phrase_id = p.id

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

    def test_paint_page(self):
        response = self.client.get('/paint/1')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Fancy-words-paint' in response.get_data(as_text=True))
        self.assertTrue('inextricably intertwined' in response.get_data(
            as_text=True))

    def test_paint_get_figure(self):
        coordinates='''
{
"x": [13.559311700517673, 13.58897501621641, 13.625276360891608, 13.66821573454328, 13.717793137171416, 13.774008568776022, 13.836862029357096, 13.906353518914635, 13.982483037448645, 14.065250584959122, 14.154656161446066, 14.250699766909483, 14.353381401349361, 14.462701064765708, 14.578658757158525, 14.701254478527808, 14.83048822887356, 14.96636000819578, 15.108869816494465, 15.258017653769622, 15.413803520021247, 15.576227415249338, 15.745289339453898, 15.920989292634921, 16.10332727479242, 16.29230328592638, 16.487917326036815, 16.69016939512371, 16.899059493187075, 17.114587620226914, 17.336753776243214, 17.565557961235985, 17.801000175205225, 18.04308041815093, 18.2917986900731, 18.54715499097174, 18.809149320846853, 19.07778167969843, 19.353052067526473, 19.63496048433099, 19.92350693011197, 20.218691404869418, 20.52051390860333, 20.82897444131372, 21.14407300300057, 21.46580959366389, 21.79418421330368, 22.129196861919933, 22.47084753951266, 22.819136246081847, 23.174062981627507, 23.535627746149636, 23.903830539648233, 24.278671362123294, 24.660150213574823, 25.048267094002824, 25.443022003407293, 25.844414941788227, 26.252445909145628, 26.667114905479497],
"y": [18.253369418822174, 18.606243816408448, 18.936281885019604, 19.24348362465566, 19.5278490353166, 19.78937811700243, 20.028070869713154, 20.243927293448767, 20.436947388209273, 20.607131153994665, 20.75447859080495, 20.878989698640133, 20.9806644775002, 21.059502927385154, 21.115505048295002, 21.14867084022974, 21.159000303189373, 21.14649343717389, 21.1111502421833, 21.0529707182176, 20.971954865276796, 20.86810268336088, 20.741414172469852, 20.591889332603714, 20.41952816376247, 20.224330665946116, 20.006296839154654, 19.765426683388082, 19.501720198646396, 19.215177384929603, 18.905798242237704, 18.57358277057069, 18.218530969928576, 17.840642840311347, 17.439918381719004, 17.016357594151557, 16.569960477608998, 16.100727032091335, 15.608657257598558, 15.093751154130672, 14.556008721687679, 13.995429960269572, 13.41201486987636, 12.80576345050804, 12.176675702164605, 11.524751624846065, 10.849991218552413, 10.152394483283652, 9.43196141903978, 8.688692025820803, 7.922586303626717, 7.133644252457516, 6.321865872313211, 5.4872511631937915, 4.629800125099268, 3.7495127580296357, 2.8463890619848877, 1.920429036965037, 0.9716326829700699, 0.0]
}
'''
        with self.app.app_context(), self.app.test_request_context():
            response = self.client.get(url_for(
                'paint.get_figure', coord=coordinates
                ))

        self.assertEqual(response.status_code, 200)
        self.assertTrue('fig'  in response.get_data(as_text=True))
        self.assertTrue('<g class='  in response.get_data(as_text=True))
        self.assertTrue('deletable'  in response.get_data(as_text=True))
