import asyncio
import json
import os
import time
from dotenv import load_dotenv
from telebot import TeleBot
import websockets

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = TeleBot(BOT_TOKEN)

# Store recent tokens with timestamp to prevent repeat alerts
recent_tokens = {}

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
            print("Received message")
            try:
                data = json.loads(message)
                print("Data:", json.dumps(data, indent=2))

                token_name = data.get('name', 'Unknown')
                token_address = data.get('mint', 'Unknown')
                liquidity = data.get('marketCapSol', 'Not provided')

                now = time.time()

                # Skip duplicates seen in last 60 seconds
                if token_address in recent_tokens and now - recent_tokens[token_address] < 60:
                    continue

                recent_tokens[token_address] = now

                msg = f"🔥 New token launched!\nName: {token_name}\nAddress: {token_address}\nMarket Cap (SOL): {liquidity}"
                if CHAT_ID:
                    bot.send_message(CHAT_ID, msg)
                    print("Sent message to Telegram")

                # Clean old entries
                for k in list(recent_tokens.keys()):
                    if now - recent_tokens[k] > 300:
                        del recent_tokens[k]

                await asyncio.sleep(1)
            except Exception as e:
                print("Error parsing message:", e)

if __name__ == "__main__":
    print("Starting bot...")
    asyncio.run(pumpfun_listener())
