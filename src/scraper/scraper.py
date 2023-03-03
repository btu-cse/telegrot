import requests
from bs4 import BeautifulSoup
from src.common.logger import Logger


class Scraper:
    site_url: str = "https://mdbf.btu.edu.tr/tr/bilgisayar/duyuru/birim/193"

    @staticmethod
    def get_announcement_id(announcement: int) -> str:
        try:
            page = requests.get(Scraper.site_url)
            soup = BeautifulSoup(page.content, 'html.parser')
            ann_list= soup.find_all('div',class_ = "ann-list")[0].find_all('ul')[0]
            anns = ann_list.find_all('li')

            
            i=0
            for val in anns:
                if i==announcement:
                    return val.find_all('a')[0].get('href').split('/')[7]
                i+=1
                

        except Exception as e:
            Logger.error("there is an error while getting announcement id from website, Announcement number: {0} \n".format(
                announcement), e)

        return ""
    
    @staticmethod
    def get_last_announcement_id() -> str:
        return Scraper.get_announcement_id(0)
    
    # gets last announcement's content: developed for sent the last announcement as a content
    @staticmethod
    def get_announcement_content_by_id(announcement: str) -> str:
        try:
            

            page = requests.get(Scraper.site_url)
            soup = BeautifulSoup(page.content, 'html.parser')
            ann_list= soup.find_all('div',class_ = "ann-list")[0].find_all('ul')[0]
            anns = ann_list.find_all('li')
        
            ann=""
        
        
            for val in anns:
                if announcement in val.find_all('a')[0].get('href').split('/')[7]:
                    ann_id=val.find_all('a')[0].get('href')
            
        
            ann_page=requests.get(ann_id, verify=False)
            soup = BeautifulSoup(ann_page.content, 'html.parser')
            ann_text= soup.find_all('div',class_ = "page-about")[0].get_text()
            ann_text += '\nİncelemek için: ' + str(ann_id) + '?'
                        
            return ann_text

        except Exception as e:
            Logger.error("there is an error while getting announcement's content from website, Announcement number: {0}".format(
             announcement), e)

            return ""


                
            

                
            
            
            
            
            


            
            

