
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

        # 🔒 Dev wallet filter
        if isinstance(dev_score, str):
            if dev_score.lower() in ["scam", "suspicious"]:
                return False
            # allow "unknown"
        elif isinstance(dev_score, (int, float)):
            if dev_score < 40:
                return False

        # 💧 Liquidity threshold
        if liquidity < 200:
            return False

        # 💸 Market cap minimum
        if market_cap < 2000:
            return False

        return True

    except Exception as e:
        print("❌ Error in legit check:", e)
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
    last_ping_time = time.time()
    ping_interval = 1800  # every 30 mins (in seconds)
    scanned_since_last_ping = 0

    while True:
        print("🔄 Scanning for new tokens...")
        tokens = fetch_new_tokens()
        scanned_since_last_ping += len(tokens)

        for token in tokens:
            name = token.get("name", "Unknown")
            symbol = token.get("symbol", "???")
            token_address = token.get("address") or f"{name}-{symbol}"
            print(f"👀 Checking: {name} | Symbol: {symbol} | ID: {token_address}")

            if token_address not in seen_tokens and is_legit_token(token):
                seen_tokens.add(token_address)
                alert_message = format_alert(token)
                send_alert(alert_message)

        # 🔁 Send heartbeat if no legit tokens
        if time.time() - last_ping_time >= ping_interval:
            status_msg = f"🧠 Sniper status: Scanned {scanned_since_last_ping} tokens — no legit hits yet."
            send_alert(status_msg)
            last_ping_time = time.time()
            scanned_since_last_ping = 0

        time.sleep(15)  # wait before next scan


        for token in tokens:
            name = token.get("name", "Unknown")
            symbol = token.get("symbol", "???")
            token_address = token.get("address") or f"{name}-{symbol}"
            print(f"👀 Checking: {name} | Symbol: {symbol} | ID: {token_address}")

            if token_address not in seen_tokens and is_legit_token(token):
                seen_tokens.add(token_address)
                alert_message = format_alert(token)
                send_alert(alert_message)

        time.sleep(15)  # check every 15 seconds

if __name__ == "__main__":
    main()
