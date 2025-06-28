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

async def pumpfun_listener():
    uri = "wss://pumpportal.fun/api/data"
    print("Connecting to websocket...")
    async with websockets.connect(uri) as ws:
        print("Connected!")

        # Subscribe to token creation events
        await ws.send(json.dumps({"method": "subscribeNewToken"}))
        print("Subscribed to new token events")

        # Subscribe to migration events
        await ws.send(json.dumps({"method": "subscribeMigration"}))
        print("Subscribed to migration events")

        async for message in ws:
            try:
                data = json.loads(message)
                print("DEBUG FULL MESSAGE:")
                print(json.dumps(data, indent=2))

                # You can add filtering here once we confirm the exact shape

            except Exception as e:
                print("Error parsing message:", e)

if __name__ == "__main__":
    print("Starting bot...")
    asyncio.run(pumpfun_listener())
