
import os
import requests
import time
from dotenv import load_dotenv
from telebot import TeleBot

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = TeleBot(BOT_TOKEN)
USER_ID = 1851186133  # your Telegram user ID

def send_alert(message):
    bot.send_message(chat_id=USER_ID, text=message, parse_mode="Markdown", disable_web_page_preview=True)

def fetch_new_tokens():
    try:
        response = requests.get("https://api.pump.fun/v1/tokens/recent")
        return response.json().get("tokens", [])
    except Exception as e:
        print("Error fetching tokens:", e)
        return []

def is_legit_token(token):
    try:
        liquidity = token.get("liquidity", 0)
        market_cap = token.get("market_cap", 0)
        dev_score = token.get("dev_wallet_score", "Unknown")
        return (
            liquidity >= 500 and
            10000 <= market_cap <= 100000 and
            dev_score != "Scam"
        )
    except:
        return False


def format_alert(token):
    name = token.get("name", "Unknown")
    symbol = token.get("symbol", "")
    liquidity = token.get("liquidity", 0)
    market_cap = token.get("market_cap", 0)
    chart = token.get("dexscreener", "#")
    address = token.get("address", "#")
    dev_score = token.get("dev_wallet_score", "Unknown")

    msg = f"""⚠️ *New Solana Token Alert*

*Name:* {name}
*Symbol:* ${symbol}
*Liquidity:* ${liquidity:,}
*Market Cap:* ${market_cap:,}
*Dev Wallet Score:* {dev_score} ✅

[View Chart]({chart})
[Token Address](https://solscan.io/token/{address})
"""
    return msg


def main():
    seen_tokens = set()
    while True:
	print("🔍 Scanning for new tokens...")
        tokens = fetch_new_tokens()
        for token in tokens:
            token_address = token.get("address")
            if token_address not in seen_tokens and is_legit_token(token):
                seen_tokens.add(token_address)
                alert_message = format_alert(token)
                send_alert(alert_message)
        time.sleep(15)  # check every 15 seconds

if __name__ == "__main__":
    main()
