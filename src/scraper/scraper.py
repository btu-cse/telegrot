import requests
from bs4 import BeautifulSoup
from common.logger import Logger

logger = Logger.getLogger()

class Scraper:
    site_url: str = 'http://bilgisayar.btu.edu.tr/index.php'

    # gets announcement id: developed for getting last announcement and serializing it
    # if announcement = 0 then gets the last announcement id
    # if announcement = 1 then gets the last-1 announcement id
    @staticmethod
    def get_announcement_id(announcement: int) -> int:
        try:
            params = {'page': 'duyuru'}

            page = requests.get(Scraper.site_url, params=params, verify=False)
            soup = BeautifulSoup(page.content, 'html.parser')
            container = soup.find_all("div", {"class": "container"})[1]
            row = container.find_all("div", {"class": "row"})[0]
            column = row.find_all("div", {"class": "col-md-9"})[0]

            i = 0
            for val in column.find_all('table'):
                if i == announcement:
                    return int(val.find_all('a')[0].get('href').split('&')[1].split('=')[1])
                i += 1

        except Exception as e:
            logger.error("Siteden duyuru getirilirken bir sorun oluştu, DUYURU NO: {0} \n {1}".format(
                announcement, e))

        return -1

    # gets last announcement's content: developed for sent the last announcement as a content
    @staticmethod
    def get_announcement_content_by_id(announcement: int) -> str:
        try:
            params = {'page': 'duyuru', 'id': announcement}

            page = requests.get(Scraper.site_url, params=params, verify=False)
            soup = BeautifulSoup(page.content, 'html.parser')
            container = soup.find_all("div", {"class": "container"})[1]
            row = container.find_all("div", {"class": "row"})[0]
            column = row.find_all("div", {"class": "col-md-9"})[0]

            panel = column.find_all("div", {"class": "panel"})[0]
            panel_body = panel.find_all('div')[1].get_text()
            panel_body += '\nİncelemek için: ' + str(Scraper.site_url) + '?'

            for val in params.keys():
                panel_body += str(val) + '=' + str(params[val]) + '&'

            return panel_body.rstrip('&')
        except Exception as e:
            logger.error("Siteden duyurunun içeriği getirilirken bir sorun oluştu, DUYURU NO: {0} \n {1}".format(
                announcement, e))

        return ""
