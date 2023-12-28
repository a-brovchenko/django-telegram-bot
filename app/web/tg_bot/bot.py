import os
from telebot import types
import telebot
from telegram_bot_pagination import InlineKeyboardPaginator
from dotenv import load_dotenv
from .main import ParseNews, Users, Tags
from django.core.cache import cache
import schedule
import time
import logging
import threading
from rest_framework.authtoken.models import Token
from .models import Users_bot

load_dotenv()
bot = telebot.TeleBot(os.environ.get("BOT_TOKEN"))


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📰 World news")
    btn2 = types.KeyboardButton("✅ My subscriptions")
    btn3 = types.KeyboardButton("📨 News without subscription")
    markup.add(btn1, btn2)
    markup.add(btn3)
    text = f"Hello !!!\nI'm a news bot who wants to share breaking news with you"
    bot.send_message(message.chat.id, text, parse_mode='html', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def main(call):
    # pagination
    if f"{call.data.split('#')[0]}" in list(cache.keys('*')): 
        page = int(call.data.split('#')[1])
        send_news_user(call.data.split('#')[0], page, call.message.chat.id, call.message.message_id)

    #return start page
    elif call.data == 'start':
        start(call.message)

    #deleting user data from the database
    elif call.data == "🚫 Unsubscribe":
        del_user = Users()
        user = del_user.get_show_user(call.message.chat.id)
        if user:
            del_user.get_delete_user(id_user=call.message.chat.id)
            bot.send_message(call.message.chat.id, '🚫 You have unsubscribed from the newsletter ', parse_mode='html')

        else:
            bot.send_message(call.message.chat.id, 'You are not subscribed', parse_mode='html')

    #delete selected tag
    elif call.data == "❌ Delete tag":
        text = "Enter the tag you want to unsubscribe from"
        message = bot.send_message(call.message.chat.id, text, parse_mode='html')
        bot.register_next_step_handler(message, delete_tag)


    # add user data from the database
    elif call.data == "✅ Subscribe":
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("✅ Add tag", callback_data='✅ Add tag')
        markup.add(btn1)
        text = "Enter the tag for which you want to receive news"
        message = bot.send_message(call.message.chat.id, text, parse_mode='html')
        bot.register_next_step_handler(message, add_tags_in_db)

    # add selected tag
    elif call.data == "✅ Add tag":

        tag_add = bot.send_message(call.message.chat.id, ' Please enter a tag', parse_mode='HTML')
        bot.register_next_step_handler(tag_add, add_tags_in_db)

    elif call.data == '📨 Show token':
        user = Users()
        user_token = user.get_show_user(id_user=call.message.chat.id)
        user_token = user_token.first()
        if user_token.token == 'False':
            text = "You don't have a token\nPlease generate it"
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton('✅ Generate token', callback_data='✅ Generate token')
            btn2 = types.InlineKeyboardButton('⬅️Back', callback_data='start')
            markup.add(btn1, btn2)
            bot.send_message(call.message.chat.id, text, parse_mode='html', reply_markup=markup)

        else:
            text = f"Your token:\n{user_token.token}"
            bot.send_message(call.message.chat.id, text, parse_mode='html')

    elif call.data == '✅ Generate token':

        user = Users_bot.objects.get(telegram_id=call.message.chat.id)
        token, created = Token.objects.get_or_create(user=user)
        user.token = token.key
        user.save()
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('⬅️Back', callback_data='start')
        markup.add(btn1)
        text = f"Your token:\n{token}"
        bot.send_message(call.message.chat.id, text, parse_mode='html', reply_markup=markup)
        

@bot.message_handler(content_types=['text'])
def get_user_text(message):
    if message.text == '📰 World news':
        send_news_user(tags_news='World', id_user=message.chat.id)
        
    elif message.text == '✅ My subscriptions':
        user = Users()
        user = user.get_show_user(message.chat.id)
        if user:
            tag = Tags()
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton('✅ Add tag', callback_data='✅ Add tag')
            btn2 = types.InlineKeyboardButton('❌ Delete tag', callback_data='❌ Delete tag')
            btn3 = types.InlineKeyboardButton('🚫 Unsubscribe', callback_data='🚫 Unsubscribe')
            btn4 = types.InlineKeyboardButton('📨 Show token', callback_data='📨 Show token')
            markup.add(btn1, btn2)
            markup.add(btn3)
            markup.add(btn4)
            user_tags = tag.get_show_tags(message.chat.id)
            if user_tags:
                user_tags = '\n'.join(tag.get_show_tags(message.chat.id))
                bot.send_message(message.chat.id, f"You are subscribed to:\n{user_tags}",
                                    parse_mode='HTML',
                                    reply_markup=markup)
            else:
                markup = types.InlineKeyboardMarkup()
                btn1 = types.InlineKeyboardButton('✅ Add tag', callback_data='✅ Add tag')
                btn2 = types.InlineKeyboardButton('🚫 Unsubscribe', callback_data='🚫 Unsubscribe')
                markup.add(btn1, btn2)
                bot.send_message(message.chat.id, "You don't have tags", parse_mode='HTML', reply_markup=markup)

        else:
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton('✅ Subscribe', callback_data='✅ Subscribe')
            btn2 = types.InlineKeyboardButton('⬅️ Back', callback_data='start')
            markup.add(btn1, btn2)
            text = 'You are not subscribed to the bot, to receive news, please subscribe'
            bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)

    elif message.text == "📨 News without subscription":
        news = bot.send_message(message.chat.id, 'Please enter the title of the news,\n'
                                                 'The request may take some time.', parse_mode='HTML')
        bot.register_next_step_handler(news, news_without_subscription)


def news_without_subscription(tag):
    tag.text = tag.text.title()
    send_news_user(tags_news=tag.text, id_user=tag.chat.id)


def add_tags_in_db(message):
    tag = Tags()
    if tag.get_check_tags(id_user=message.chat.id, user_tag=message.text):
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("✅ Add another tag", callback_data='✅ Add tag')
        btn2 = types.InlineKeyboardButton("⬅️Back", callback_data='start')
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, 'You have already added a tag', parse_mode='HTML', reply_markup=markup)
    
    else:
        user = Users()
        if not user.get_show_user(id_user=message.chat.id):
            user.get_add_user(message.chat.id)
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("✅ Add another tag", callback_data='✅ Add tag')
        btn2 = types.InlineKeyboardButton("⬅️Back", callback_data='start')
        btn3 = types.InlineKeyboardButton('Show token', callback_data='📨 Show token')
        markup.add(btn1, btn2)
        markup.add(btn3)
        tag.get_add_tags(id_user=message.chat.id, tag=message.text)
        bot.send_message(message.chat.id, f"Tag {message.text} added successfully", parse_mode="HTML", reply_markup=markup)


def delete_tag(message):
    tag = Tags()
    tag.get_delete_tags(message=message)
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("❌ Delete another tag", callback_data='❌ Delete tag')
    btn2 = types.InlineKeyboardButton("⬅️Back", callback_data='start')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, f"Tag removed", parse_mode="HTML", reply_markup=markup)


def list_news_in_cache(tag):
    my_list = cache.get(tag)
    if my_list is None:
        news = ParseNews()
        my_list = news.get_show_news(tag)
        if len(my_list) > 0:
            cache.set(tag, my_list, timeout=300)

    return my_list


def send_news_user(tags_news=None, page=None, id_user=None, message_id=None):
    news = list_news_in_cache(tag=tags_news)
    if len(news) <= 0:
        bot.send_message(id_user, f"No new news for your tag - <b>{tags_news}</b>", parse_mode='HTML')

    else:
        pages = [f"<b>News by tag {tags_news}\n\n" 
                     f"{x[0]}</b>\n\n<b>" 
                     f"<a href='{x[1]}'>Source</a></b>\n\n" for x in news]
        
        paginator = InlineKeyboardPaginator(
            len(pages),
            current_page=page,
            data_pattern=f"{tags_news}#{{page}}"
        )

        if not page:
            bot.send_message(
                id_user, pages[0], 
                reply_markup=paginator.markup, 
                parse_mode='HTML'
            )  
        else:
            bot.edit_message_text( 
                chat_id=id_user,
                message_id=message_id,
                text=pages[page - 1],
                reply_markup=paginator.markup,
                parse_mode='HTML'
            )
    
    
def schedule_add_news_in_db():
    print('add news in db')
    tag = Tags()
    news = ParseNews()
    news.get_delete_old_news()
    [news.get_add_news(news=news.get_search_news(x), check_list=news.get_check_news(x)) for x in tag.get_show_tags()]


def schedule_sending_news():
    print('sending news')
    user = Users()
    tag = Tags()
    news = { x:tag.get_show_tags(x) for x in user.get_all_users() if x != None }

    for id in news:
        for tags in news[id]:
            send_news_user(tags_news=tags, id_user=id)


def thread():
    print('thread start')
    #add new news and delete older than 6 hours
    schedule.every(60).minutes.do(schedule_add_news_in_db)
    

    # Tasks by UTC
    schedule.every().day.at("10:00").do(schedule_sending_news)
    schedule.every().day.at("18:00").do(schedule_sending_news)
   

    while True:
        schedule.run_pending()
        time.sleep(1)

def run_bot():
    print('bot started')
    thr1 = threading.Thread(target=bot.polling, args=(True,)).start()
    thr = threading.Thread(target=thread, name='Daemon', daemon=True).start()
