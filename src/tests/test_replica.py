import unittest

# from bs4 import BeautifulSoup

from src.scraper.scraper import Scraper


class TestScraper(unittest.TestCase):

    def test_get_announcement_id(self):
        announcement = 1
        print(Scraper.get_announcement_id(announcement))

    def test_get_announcement_content_by_id(self):
        announcement = 1
        announcement_id = Scraper.get_announcement_id(announcement)
        print(Scraper.get_announcement_content_by_id(announcement_id))

if __name__ == '__main__':
    unittest.main()
