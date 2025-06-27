import os
import telebot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    print(f"Chat ID: {message.chat.id}")
    bot.send_message(message.chat.id, f"Your chat ID is: {message.chat.id}")

print("Send a message to your bot to get your chat ID...")
bot.polling()
