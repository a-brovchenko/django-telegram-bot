import re
from bs4 import BeautifulSoup as bs
import requests
from datetime import datetime, timedelta
import django
django.setup()
from .models import News_bot, Users_bot, Tags_bot
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
from django.db.utils import DataError
from json_logger_stdout import JSONLoggerStdout
import socket
import undetected_chromedriver as uc

class ParseNews:
    
    """Class for parsing and working with news"""

    logger = JSONLoggerStdout(
        container_id=socket.gethostname(),
        container_name="BOT"
    )
    
    def get_search_news(self, value):

        return self.abc_news(value) + self.ndtv_news(value) + self.the_sun_news(value)

    
    def selenium_option(self):
        options = uc.ChromeOptions()
        options.headless=True
        options.add_argument("--headless")
        #options.add_argument("--no-sandbox")
        options.add_argument("--no-proxe-server")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        response = uc.Chrome(options=options,driver_executable_path="/usr/bin/chromedriver")
        return response


    def abc_news(self, tag):

        news_list = []

        tag = tag.title()
        if len(tag.split()) > 1:
            tag = '%2520'.join(tag.split())

        response = self.selenium_option()
        response.get(f"https://abcnews.go.com/search?searchtext={tag}&after=today")
        html_page = response.find_elements(By.CSS_SELECTOR, "section.ContentRoll__Item")

        pattern = re.compile(r"([Ii]n\s)?((\b[1-6]\shours?\s(ago)?)|(\d+\s(minute|second)s?))") 
        pattern_date = re.compile(r"\d+")
        for news in html_page:
            try:
                match = pattern.search(news.text)
                if match:
                    time = pattern_date.search(match.group()).group()
                    if 'hour' in match.group():
                        date_publisher = datetime.now() - timedelta(hours=int(time))
                    elif 'minute' in match.group():
                        date_publisher = datetime.now() - timedelta(minutes=int(time))
                    else:
                        date_publisher = datetime.now()
                    link = news.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')

                    news_list.append((news.text.replace('\n', ''), link, tag, date_publisher))

                else:
                    continue

            except Exception as e:
                
                self.logger.error(e)
                continue

        response.quit()
        return news_list


    def the_sun_news(self, tag):
        tag = tag.title()
        if len(tag.split()) > 1:
            tag = '+'.join(tag.split())
        news_list = []
        response = requests.get(f"https://www.the-sun.com/?s={tag}")
        soup = bs(response.content, "lxml")
        soup = soup.find_all('div', class_=re.compile(r'teaser-item teaser__large-side teaser theme-(?!betting)\w+'), limit=5)

        for news in soup:
            try:
                link = 'https://www.the-sun.com'+ news.find('a', class_='text-anchor-wrap')['href']
                response_news = requests.get(link)
                soup_page_date = bs(response_news.content, 'lxml')
                
                if soup_page_date.find('li', class_='article__updated'):
                    soup_page_date = soup_page_date.find('li', class_='article__updated').text
                else:
                    soup_page_date = soup_page_date.find('li', class_='article__published').text

                time = re.findall(r'(\d{1,2}:\d{1,2})', soup_page_date)
                day = re.findall(r'(\w{3} \d{1,2} \d{4})', soup_page_date)
                date_publisher = datetime.strptime(' '.join(day + time), "%b %d %Y %H:%M") + timedelta(hours=6)

                if date_publisher < (datetime.now() - timedelta(hours=6)):
                    continue
                else:
                    text = news.find('h3', class_='teaser__subdeck').text
                
                news_list.append((text, link, tag, date_publisher))

            except Exception as e:

                self.logger.error(e)
                continue

        return news_list


    def ndtv_news(self, tag):

        tag = tag.title()
        if len(tag.split()) > 1:
            tag = '-'.join(tag.split())
        news_list = []
        response = requests.get(f"https://www.ndtv.com/search?searchtext={tag}")
        soup = bs(response.content, "lxml")
        soup = soup.find_all('li', class_='src_lst-li', limit=8)
        for news in soup:
            try:
                link = news.find('a')['href']

                if 'https://www.ndtv.com' in link:
                    page = requests.get(link)
                    soup = bs(page.content, "lxml")
                    date_str = soup.find('span', {'itemprop':'dateModified'})
                    date = date_str['content']
                    date = datetime.fromisoformat(date_str['content'])
                    date = date.replace(tzinfo=None) - timedelta(hours=3, minutes=30)
                    text = ' '.join(news.text.split())

                    if date < (datetime.now() - timedelta(hours=6)):
                        continue
                    else:
                        news_list.append((text, link, tag,  date))

            except Exception as e:

                self.logger.error(e)

        return news_list


    def get_add_news(self, news, check_list):
        """add news to database"""
        for i in news:
            if i[1] not in check_list:
                try:
                    news = News_bot(news=i[0], site=i[1], tags=i[2], data_publisher=i[3])
                    news.save()
                except Exception as e:
                    if "Data too long for column 'news' at row 1" in str(e):
                        with open('long_news.txt', 'a') as f:
                            f.write(i[0])
                            f.write('\n')
                            f.close()
                        self.logger.error(e)


    def get_delete_old_news(self):
        """Deleting news older than 6 hours"""

        six_hours_ago = datetime.now() - timedelta(hours=6)
        News_bot.objects.filter(add_date__lt=six_hours_ago).delete()


    def get_show_news(self, value): 
        """Show news in db, else parse news + add in db"""
        
        value = value.title()
        result = News_bot.objects.filter(tags=value)            
        if result:  # if news in db
            result = [[x.news, x.site] for x in News_bot.objects.filter(tags=value)]

        else:  # parsing sites + add news in db +  sending news to a bot 
            result = self.get_search_news(value)
            if len(result) > 0:
                check_list = self.get_check_news(value)
                self.get_add_news(news=result, check_list=check_list)
                result = [[x[0], x[1]] for x in result]

        return result
    

    def get_check_news(self, value):
        """Check for duplicates"""
        result = News_bot.objects.filter(tags=value).values_list('site', flat=True)
        return result


class Users:
    """Class for working with user"""

    def get_add_user(self, id_user):
        """Adds users to the database"""
        Users_bot(telegram_id=id_user).save()


    def get_delete_user(self, id_user):
        """Delete users to the database"""
        user_to_delete = Users_bot.objects.filter(telegram_id=id_user).delete()


    def get_show_user(self, id_user):
        result = Users_bot.objects.filter(telegram_id=id_user)
        return result
    

    def get_all_users(self):
        return list(Users_bot.objects.values_list('telegram_id', flat=True))


class Tags:

    """Class for working with tag"""

    def get_add_tags(self, id_user, tag):
        """Adds tag to Database"""
        tag = tag.title()
        user = Users_bot.objects.get(telegram_id=id_user)
        Tags_bot(telegram_id=user, tags=tag).save()


    def get_delete_tags(self, message):
        Tags_bot.objects.filter(telegram_id=message.chat.id, tags=message.text.title()).delete()


    def get_check_tags(self,id_user, user_tag):

        user_tag = user_tag.title()
        tags = [x.tags for x in Tags_bot.objects.filter(telegram_id=id_user)]
        if user_tag in tags:
            return True
        
        return False



    def get_show_tags(self, id_user=None):
        """Show tags"""

        if id_user:
            result = Tags_bot.objects.filter(telegram_id=id_user)
            tags = [x.tags for x in result]
        else:
            result = Tags_bot.objects.values('tags').distinct()
            tags = [x['tags'] for x in result]
        

        return tags
    

    
