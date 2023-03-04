from this import d
import requests
from bs4 import BeautifulSoup
from src.common.logger import Logger


class Scraper:
    site_url: str = "https://mdbf.btu.edu.tr/tr/bilgisayar/duyuru/birim/193"

    @staticmethod
    def __get_content_from_url(url: str) -> str:
        return requests.get(url).content

    @staticmethod
    def get_announcement_id(announcement: int) -> int:
        try:
            content = Scraper.__get_content_from_url(Scraper.site_url)
            soup = BeautifulSoup(content, 'html.parser')
            announcement_list = soup.find_all(
                'div', class_="ann-list")[0].find_all('ul')[0]
            announcements = announcement_list.find_all('li')

            i = 0
            for val in announcements:
                if i == announcement:
                    return val.find_all('a')[0].get('href').split('/')[7]
                i += 1

        except Exception as e:
            Logger.error("there is an error while getting announcement id from website, Announcement number: {0} \n".format(
                announcement), e)

        return -1

    @staticmethod
    def get_last_announcement_id() -> int:
        return Scraper.get_announcement_id(0)

    # gets last announcement's content: developed for sent the last announcement as a content
    @staticmethod
    def get_announcement_content_by_id(announcement: int) -> str:
        try:
            content = Scraper.__get_content_from_url(Scraper.site_url)
            soup = BeautifulSoup(content, 'html.parser')
            announcement_list = soup.find_all(
                'div', class_="ann-list")[0].find_all('ul')[0]
            announcements = announcement_list.find_all('li')

            announcement_url = ""

            for val in announcements:
                if announcement in val.find_all('a')[0].get('href').split('/')[7]:
                    announcement_url = val.find_all('a')[0].get('href')

            if announcement_url == "":
                raise Exception(
                    "there is no announcement suc this: {0}".format(announcement_url))

            announcement_page = requests.get(announcement_url, verify=False)
            soup = BeautifulSoup(announcement_page.content, 'html.parser')
            announcement_text = soup.find_all('div', class_="page-about")[0].get_text()
            announcement_text += '\nİncelemek için: ' + str(announcement_url) + '?'

            return announcement_text

        except Exception as e:
            Logger.error("there is an error while getting announcement's content from website, Announcement number: {0}".format(
                announcement), e)

        return ""
