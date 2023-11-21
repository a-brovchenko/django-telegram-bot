import os
from telebot import types
import telebot
from telegram_bot_pagination import InlineKeyboardPaginator
from dotenv import load_dotenv


load_dotenv()
bot = telebot.TeleBot(os.environ.get("BOT_TOKEN"))


@bot.message_handler(commands=['start', 'help'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📰 Top news")
    btn2 = types.KeyboardButton("✅ My subscriptions")
    btn3 = types.KeyboardButton("📨 News without subscription")
    markup.add(btn1, btn2)
    markup.add(btn3)
    text = f"Hello !!!\nI'm a news bot who wants to share breaking news with you"
    bot.send_message(message.chat.id, text, parse_mode='html', reply_markup=markup)


def run_bot():
    bot.polling(non_stop=True)