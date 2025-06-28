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
        await ws.send(json.dumps({"method": "subscribeMigration"}))
        print("Subscribed to token creation and migration events")

        async for message in ws:
            try:
                data = json.loads(message)
                if data.get('txType') != 'create':
                    continue

                token_address = data.get('mint', '').strip().lower()
                if not token_address or token_address in alerted_mints:
                    continue

                alerted_mints.add(token_address)
                token_name = data.get('name', 'Unknown')
                dexscreener_link = f"https://dexscreener.com/solana/{token_address}"

                msg = (
                    f"🔥 New token bonded on pump.fun!\n"
                    f"Name: {token_name}\n"
                    f"Address: {token_address}\n"
                    f"[View on Dexscreener]({dexscreener_link})"
                )

                bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
                print("Sent alert to Telegram")

            except Exception as e:
                print("Error parsing message:", e)

if __name__ == "__main__":
    print("Starting bot...")
    asyncio.run(pumpfun_listener())
