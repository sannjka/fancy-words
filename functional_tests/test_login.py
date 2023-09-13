from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from functional_tests.base import FunctionalTest


class LoginTest(FunctionalTest):

    def test_login(self):
        # Alice is a registered user of the Fancy-words app
        # She goes to the login page
        self.client.get(self.live_server_url)
        self.client.find_element(By.LINK_TEXT, 'Log In').click()

        # The login page pops up
        self.wait_for(lambda: self.assertIn(
            'Login',
            self.client.find_element(By.TAG_NAME, 'h1').text
        ))
