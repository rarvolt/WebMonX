import os
from unittest import TestCase, skip

from ..scrapper import Scrapper


@skip
class ScrapperTest(TestCase):
    def setUp(self):
        test_file_name = os.path.join(os.path.dirname(__file__), 'test_files/test1.html')
        self.test_html = open(test_file_name).read()

    def test_content_is_set_correctly(self):
        scrapper = Scrapper(content=self.test_html)
        self.assertEqual(scrapper.get_content(), self.test_html)

        scrapper.set_content("")
        self.assertEqual(scrapper.get_content(), "")

        scrapper.set_content(content=self.test_html)
        self.assertEqual(scrapper.get_content(), self.test_html)

    def test_xpath_is_set_correctly(self):
        xpath = '//*[@class="version"]/text()'
        scrapper = Scrapper(xpath=xpath)
        self.assertEqual(scrapper.get_xpath(), xpath)

        scrapper.set_xpath("")
        self.assertEqual(scrapper.get_xpath(), "")

        scrapper.set_xpath(xpath=xpath)
        self.assertEqual(scrapper.get_xpath(), xpath)

    def test_value_is_extracted_by_xpath(self):
        xpath = '//*[@class="version"]/text()'
        scrapper = Scrapper(content=self.test_html, xpath=xpath)
        version = scrapper.get_value()
        self.assertEqual(version, '2.3.7')

        xpath = '//*[@class="revision"]/strong/text()'
        scrapper.set_xpath(xpath)
        revision = scrapper.get_value()
        self.assertEqual(revision, '1-3')

    def test_saves_extracted_xpath(self):
        xpath = '//*[@class="version"]/text()'
        scrapper = Scrapper(content=self.test_html, xpath=xpath)
        scrapper.save_value()
