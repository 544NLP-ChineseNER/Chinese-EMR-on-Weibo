import jieba.analyse
import urllib.request
from selenium import webdriver

from bs4 import BeautifulSoup

from src.common import extract_tiny_url_from_string, test_visible

class TweetNameExtractor:
    def __init__(self, *args, **kwargs):
        self.webpage_driver = webdriver.Chrome()
        pass

    def _extract_tiny_url(self, string):
        '''
        Extract tiny from tweet. Tiny URL format:
        :param (String):
        :return:
        '''
        return extract_tiny_url_from_string(string)

    def _extract_text_from_page(self, url):
        '''
        Extract visible text from a page.
        :param url: (String) page url
        :return: String: Visible text extracted from the page.
        '''

        # Read a page and extract visible text from page
        self.webpage_driver.get(url)
        html_soup = BeautifulSoup(self.webpage_driver.page_source)
        [s.extract() for s in html_soup(['style', 'script', '[document]', 'head', 'title'])]
        visible_text = html_soup.getText()

        return visible_text

    def _extract_names_from_string(self, s):
        '''
        Extract names from a given string.
        :param s: (String)
        :return: List[String]: a list of names extracted from string s
                Return an empty list if nothing was found
        '''
        res = []
        print(s)
        words = jieba.analyse.extract_tags(s, allowPOS=['nr'])
        return res

    def extract_names(self, tweet):
        '''
        Extract names from a tweet
        :param tweet: (String) content of the tweet
        :return: List[String] a list of names
                Return an empty list of no name was found
        '''
        result = []

        # Try to see if the tweet has tiny urls
        # If it has, try extracting names from the corresponding page
        urls = self._extract_tiny_url(tweet)
        for url in urls:
            page_text = self._extract_text_from_page(url)
            names_in_page = self._extract_names_from_string(page_text)
            result += names_in_page

        # Try to extract names from the tweet itself
        result += self._extract_names_from_string(tweet)

        return result


if __name__ == '__main__':
    name_extractor = TweetNameExtractor()
    name_extractor.extract_names("这个很赞～ 当爷新单 强势来袭:http://t.cn/R2cnKqK")
