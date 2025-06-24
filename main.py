import os
from dotenv import load_dotenv
import telebot
import requests

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Twinsniperbot is live! 🐐🚀")

def send_alert(chat_id, text):
    bot.send_message(chat_id, text, parse_mode="Markdown", disable_web_page_preview=True)

# Test alert function
def send_test_alert():
    message = """*New Solana Token Alert* ⚠️

*Name:* MaskWifCat
*Symbol:* $MWC
*Liquidity:* $1,250
*Market Cap:* $84,000
*Dev Wallet Score:* Legit ✅

[View Chart](https://dexscreener.com/solana/0x1234567890abcdef)
[Token Address](https://solscan.io/token/0x1234567890abcdef)
"""
    bot.send_message(chat_id=1851186133, text=message, parse_mode="Markdown", disable_web_page_preview=True)

if __name__ == "__main__":
    send_test_alert()  # Call this once to test alert
    print("Bot is running...")
    bot.polling()
