import asyncio
import json
import os
from dotenv import load_dotenv
from telebot import TeleBot
import websockets

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = TeleBot(BOT_TOKEN)

alerted_mints = set()

async def pumpfun_listener():
    uri = "wss://pumpportal.fun/api/data"
    print("Connecting to websocket...")
    async with websockets.connect(uri) as ws:
        print("Connected!")
        await ws.send(json.dumps({"method": "subscribeNewToken"}))
        print("Subscribed to new token events")
        await ws.send(json.dumps({"method": "subscribeMigration"}))
        print("Subscribed to migration events")

        async for message in ws:
            try:
                data = json.loads(message)
                if data.get('txType') != 'create':
                    continue

                token_address = data.get('mint', '').strip().lower()
                if not token_address or token_address in alerted_mints:
                    continue

                liquidity_usd = data.get('liquidityUsd', 0)
                market_cap_usd = data.get('marketCapUsd', 0)
                volume_usd = data.get('volume24hUsd', 0)

                if liquidity_usd < 10000 or market_cap_usd < 10000 or volume_usd < 10000:
                    continue

                alerted_mints.add(token_address)
                token_name = data.get('name', 'Unknown')

                dexscreener_link = f"https://dexscreener.com/solana/{token_address}"
                image_url = data.get('image', '')

                caption = (
                    f"🔥 New token launched!\n"
                    f"Name: {token_name}\n"
                    f"Address: {token_address}\n"
                    f"Liquidity (USD): {liquidity_usd}\n"
                    f"Market Cap (USD): {market_cap_usd}\n"
                    f"24h Volume (USD): {volume_usd}\n"
                    f"[View on Dexscreener]({dexscreener_link})"
                )

                if image_url:
                    bot.send_photo(CHAT_ID, image_url, caption=caption, parse_mode="Markdown")
                else:
                    bot.send_message(CHAT_ID, caption, parse_mode="Markdown")

                print("Sent message to Telegram")

            except Exception as e:
                print("Error parsing message:", e)

if __name__ == "__main__":
    print("Starting bot...")
    asyncio.run(pumpfun_listener())
