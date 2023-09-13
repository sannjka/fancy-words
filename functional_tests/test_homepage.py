from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from functional_tests.base import FunctionalTest


class HomePageTest(FunctionalTest):

    def test_homepage(self):
        # Alice has heard about a cool online Fancy-words app
        # She goes to check out its hamepage
        self.client.get(self.live_server_url)

        # She notices the page title Fancy-words and header Arbitrarily 
        # selected word
        self.assertIn('Fancy-words', self.client.title)
        header_text = self.client.find_element(By.TAG_NAME, 'h3').text
        self.assertIn('Arbitrarily selected phrase', header_text)
