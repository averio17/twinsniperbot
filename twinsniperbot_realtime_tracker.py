
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

def fetch_birdeye_tokens():
    try:
        url = "https://public-api.birdeye.so/public/tokenlist?sort=createdAt"
        headers = {"accept": "application/json"}

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return []

        raw_tokens = response.json().get("data", [])
        tokens = []

        for item in raw_tokens[:100]:
            token = {
                "name": item.get("name", "Unknown"),
                "symbol": item.get("symbol", ""),
                "address": item.get("address", ""),
                "liquidity": item.get("liquidity", 0),
                "market_cap": item.get("market_cap", 0),
                "dexscreener": item.get("url", "#"),
                "dev_wallet_score": "Unknown",  # fallback
                "source": "birdeye"
            }
            tokens.append(token)

        return tokens
    except Exception as e:
        print("❌ Error fetching Birdeye tokens:", e)
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
    ping_interval = 1800  # every 30 mins
    scanned_since_last_ping = 0

    while True:
    print("🛰 Scanning for new tokens...")

    pump_tokens = fetch_new_tokens()
    birdeye_tokens = fetch_birdeye_tokens()
    tokens = pump_tokens + birdeye_tokens

    print(f"📦 Fetched {len(tokens)} tokens total")

    legit_hits = 0
    scanned_this_round = 0

    for token in tokens:
        name = token.get("name", "Unknown")
        symbol = token.get("symbol", "???")
        address = token.get("address", "")
        print(f"👀 Checking: {name} | Symbol: {symbol} | ID: {address}")

        if address not in seen_tokens and is_legit_token(token):
            scanned_this_round += 1
            legit_hits += 1
            seen_tokens.add(address)
            alert_message = format_alert(token)
            send_alert(alert_message)

    # 💓 Heartbeat if no legit tokens
    if time.time() - last_ping_time >= ping_interval:
        if legit_hits == 0:
            status_msg = f"🛰 Sniper status: Scanned {len(tokens)} tokens — no legit hits yet"
            print(status_msg)
            send_alert(status_msg)

        last_ping_time = time.time()
        scanned_since_last_ping = 0

    time.sleep(15)  # wait before next scan




        time.sleep(15)  # check every 15 seconds

if __name__ == "__main__":
    main()
