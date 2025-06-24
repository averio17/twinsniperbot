import os
import telebot
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Twinsniperbot is live! 💸🚀")

def send_alert(chat_id, text):
    bot.send_message(chat_id, text)

if __name__ == '__main__':
    print("Bot is running...")
    bot.polling()
