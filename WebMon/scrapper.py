from lxml import html


class Scrapper(object):
    def __init__(self, content: str = None, xpath: str = None):
        self.content = content
        self.xpath = xpath
        self.value = None

    def get_value(self):
        self._extract_xpath()
        return self.value

    def set_xpath(self, xpath: str):
        self.xpath = xpath

    def get_xpath(self) -> str:
        return self.xpath

    def set_content(self, content: str):
        self.content = content

    def get_content(self) -> str:
        return self.content

    def _extract_xpath(self):
        tree = html.fromstring(self.content)  # type: html
        self.value = ' '.join(tree.xpath(self.xpath))
