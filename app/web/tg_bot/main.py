import os
import re
from bs4 import BeautifulSoup as bs
import json
import requests
from datetime import datetime, timedelta
from .models import News, User

class ParseNews:

    """Class for parsing and working with news"""

    def get_search_news(self, value):

        """Search by sites from the database file 'search.json'"""

        value = value.title()
        list_news = []

        # open file
        file_path = os.path.join(os.path.dirname(__file__), 'search.json')

        with open(file_path, "r") as file:
            filer = file.read()
            dict_news = json.loads(filer)

        for news in dict_news:
            # Check word
            if len(value.split()) > 1:
                driver = requests.get(news["site"].format(f"{news['search']}".join(value.split())))
            else:
                driver = requests.get(news["site"].format(value))

            # get html and tags
            soup = bs(driver.content, "lxml")
            tags = news["text"].split("class_=")
            datatags = news["date"].split("class_=")
            res = soup.find_all(tags[0], class_=tags[1], limit=3)
            current_date_minus_six_hours = datetime.now() - timedelta(hours=48)

            for i in res:
                date = i.find(datatags[0], class_=datatags[1]).get_text(strip=True, separator=' ')
                
                date = self.get_public_date(date, news['site'])
        
                if date >= current_date_minus_six_hours:
                    if date >= current_date_minus_six_hours:
                        if 'http' in i.a.get('href'):
                            list_news.append([i.a.get_text(strip=True, separator=' ').replace("\xa0", ""),
                                                i.a.get("href"), value, date])
                        else:
                            link = re.match(r"^h.*\.(com|uk|org|ca)", news["site"]).group()
                            list_news.append([i.a.get_text(strip=True, separator=' '),
                                                link + i.a.get("href"), value, date])
                        
        return list_news


    def get_today_data(self):
        today = str(datetime.today().date())
        data = datetime.strptime(today, '%Y-%m-%d')
        return datetime.timestamp(data)


    def get_public_date(self, value, site):
    
        """Convert publication date to string"""
        if len(value) == 0:
            return datetime.now()
        
        elif "www.ndtv.com" in site:
            date = re.search(r'\w+\s{1,2}\d{1,2}, \d{4}', value).group()
            date = datetime.strptime(date, '%B %d, %Y')
            return date
        
        elif "globalnews" in site:
            if 'hours' in value or 'hour' in value:
                return datetime.now()
            else:
                date = re.search(r'\w{3} \d{1,2}', value).group()
                date = f'{date} {datetime.now().year}'
                date = datetime.strptime(date, '%b %d %Y')
                return date

   
    def get_add_news(self, value):
        """add news to database"""
        
        list_news = self.get_search_news(value)
        check_list = self.get_check_news(value)
     
        # Insert new values
        for i in list_news:
            if i[1] not in check_list:
                news = News(news=i[0], site=i[1], tags=i[2], data_publisher=i[3])
                news.save()


    def get_delete_old_news(self):
        """Deleting news older than 6 hours"""

        six_hours_ago = datetime.now() - timedelta(hours=6)
        News.objects.filter(add_date__lt=six_hours_ago).delete()


    def get_show_news(self, value):
            value = value.title()
            result = [[x.news, x.site] for x in News.objects.filter(tags=value)]
            return result


    def get_all_tags_in_db(self):
        """Get all tags in json"""

        result = {'tags' : [x['tags'] for x in News.objects.values('tags').distinct()]}
        return result


    def get_all_news_in_db(self):
        """Get all news in json"""

        result = {'news': [x.news for x in News.objects.all()]}
        return result


    def get_check_news(self, value):
        """Check for duplicates"""
        
        result = News.objects.filter(tags=value).values_list('site', flat=True)
        print(result)

        return result

class Users:
    """Class for working with user"""

    def get_add_user(self, value, token=None):
        """Adds users to the database"""
       
        if not token:
            user = User(telegram_id=value)
        elif token:
            user= User.objects.get(id=value)
            user.token = token
            user.save()


    def get_delete_user(self, value):
        """Delete users to the database"""
        user_to_delete = User.objects.filter(id=value).delete()


    def get_check_user(self, value):
        """Check for record availability"""
        if User.objects.get(id=value):
            return True
        else:
            return False
        
