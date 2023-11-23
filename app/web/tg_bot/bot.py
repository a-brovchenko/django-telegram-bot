import os
from telebot import types
import telebot
from telegram_bot_pagination import InlineKeyboardPaginator
from dotenv import load_dotenv
from .main import ParseNews, Users, Tags, SendData
from django.core.cache import cache
import schedule
import time


load_dotenv()
bot = telebot.TeleBot(os.environ.get("BOT_TOKEN"))


@bot.message_handler(commands=['start', 'help'])
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
    if f":1:{call.data.split('#')[0]}" in list(cache._cache.keys()):
        page = int(call.data.split('#')[1])
        send_news_user(call.data.split('#')[0], page, call.message.chat.id, call.message.message_id)


@bot.message_handler(content_types=['text'])
def get_user_text(message):
    if message.text == '📰 World news':
        send_news_user(tags_news='World', id_user=message.chat.id)

    elif message.text == "📨 News without subscription":
        news = bot.send_message(message.chat.id, 'Please enter the title of the news,\n'
                                                 'The request may take some time.', parse_mode='HTML')
        bot.register_next_step_handler(news, news_without_subscription)


def news_without_subscription(tag):
    tag.text = tag.text.title()
    send_news_user(tags_news=tag.text, id_user=tag.chat.id)



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
    
    
def run_bot():
    bot.polling(non_stop=True)