import os
import time
import unittest
import threading
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from werkzeug.serving import make_server
from app import db, create_app
from app.models import User, Phrase, WordList


MAX_WAIT = 10
SCREEN_DUMP_LOCATION = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'screendumps'
)

def wait(fn):
    def modified_fn(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return fn(*args, **kwargs)
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)
    return modified_fn

class FunctionalTest(unittest.TestCase):
    host = 'localhost'
    port = '5004'

    @classmethod
    def setUpClass(cls):
        # start Chrome
        options = Options()
        options.binary_location =\
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        options.add_argument('headless')
        cls.client = webdriver.Chrome(options=options)

        # skip these tests if the browser could not be started
        if cls.client:

            # get app url
            cls.live_server_url = 'http://' + cls.host + ':' + cls.port
            cls.staging_server = os.environ.get('STAGING_SERVER')
            if cls.staging_server:
                print('on staging')
                cls.live_server_url = 'http://' + cls.staging_server
            else:
                # create the application
                cls.app = create_app('testing')
                cls.app_context = cls.app.app_context()
                cls.app_context.push()
                # suppress logging to keep tests output clean
                import logging
                logger = logging.getLogger('werkzeug')
                logger.setLevel('ERROR')
                # create the database and populate with some fake data
                db.create_all()
                # ...
                # start the Flask server in a thread
                cls.server = make_server(cls.host, cls.port, cls.app)
                cls.server_thread = threading.Thread(
                    target=cls.server.serve_forever,
                )
                cls.server_thread.start()
                time.sleep(1)


    @classmethod
    def tearDownClass(cls):
        if cls.client and not cls.staging_server:
            # stop the Flas server and the browser
            cls.server.shutdown()
            cls.client.quit()
            cls.server_thread.join()
            # destroy database
            db.drop_all()
            db.session.remove()
            # remove application context
            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTests('Web browser not available')

    def tearDown(self):
        if self._test_has_failed():
            if not os.path.exists(SCREEN_DUMP_LOCATION):
                os.makedirs(SCREEN_DUMP_LOCATION)
            for ix, handle in enumerate(self.client.window_handles):
                self._windowid = ix
                self.client.switch_to.window(handle)
                self.take_screenshot()
                self.dump_html()

    def _test_has_failed(self):
        return any(error for (method, error) in self._outcome.errors)

    def take_screenshot(self):
        filename = self._get_filename() + '.png'
        print('screenshotting to', filename)
        self.client.get_screenshot_as_file(filename)

    def dump_html(self):
        filename = self._get_filename() + '.html'
        print('dumping page HTML to', filename)
        with open(filename, 'w') as f:
            f.write(self.client.page_source)

    def _get_filename(self):
        timestamt = datetime.now().isoformat().replace(':', '.')[:19]
        return '{folder}/{classname}.{method}-window{windowid}-{timestamp}'.\
            format(
                folder=SCREEN_DUMP_LOCATION,
                classname=self.__class__.__name__,
                method=self._testMethodName,
                windowid=self._windowid,
                timestamp=timestamt
            )

    @wait
    def wait_for(self, fn):
        return fn()
