import os
import re
from bs4 import BeautifulSoup as bs
import json
import requests
from datetime import datetime, timedelta
import django
django.setup()
from .models import News_bot, Users_bot, Tags_bot


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
            current_date_minus_six_hours = datetime.now() - timedelta(hours=100)

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

   
    def get_add_news(self, news, check_list):
        """add news to database"""
        
        for i in news:
            if i[1] not in check_list:
                news = News_bot(news=i[0], site=i[1], tags=i[2], data_publisher=i[3])
                news.save()


    def get_delete_old_news(self):
        """Deleting news older than 6 hours"""

        six_hours_ago = datetime.now() - timedelta(hours=6)
        News_bot.objects.filter(add_date__lt=six_hours_ago).delete()


    def get_show_news(self, value): 
            """Show news in db, else parse news + add in db"""
            
            value = value.title()
            result = News_bot.objects.filter(tags=value)            
            if result: # if news in db
                result = [[x.news, x.site] for x in News_bot.objects.filter(tags=value)]

            else: # parsing sites + add news in db +  sending news to a bot 
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
    

    # def get_dict_news(self):

    #     result = News_bot.objects.values('tags').distinct()
    #     tag = [x.tags for x in result]
    #     dict_news = dict()
    #     dict_news['Tags'] = tag

    #     return dict_news


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
        else:
            result = Tags_bot.objects.values('tag').distinct()
        
        tags = [x.tags for x in result]
        return tags
    

class SendData:

    """Class for sending data to the bot"""

    def send_data(self):

        user = Users()
        tag = Tags()
        tags_db = ParseNews()

        result = {}

        res = {x['id']: tag.get_show_tags(x['id']) for x in user.get_show_user()}
        user_tag = [{'id': i, 'tag': res[i]} for i in res]

        tags_db = tags_db.get_dict_news()['Tags']

        result['Tags_db'] = tags_db
        result['Users_tag'] = user_tag

        return result
    
    