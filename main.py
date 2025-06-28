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

seen_signatures = set()

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
                print("Full data:", json.dumps(data, indent=2))

                signature = data.get('signature', '').strip()
                if not signature:
                    continue

                if signature in seen_signatures:
                    print("Duplicate signature, skipping...")
                    continue
                seen_signatures.add(signature)

                token_name = data.get('name', 'Unknown')
                token_address = data.get('mint', 'Unknown')
                liquidity = data.get('marketCapSol', 'Not provided')

                msg = f"🔥 New token launched!\nName: {token_name}\nAddress: {token_address}\nMarket Cap (SOL): {liquidity}"
                if CHAT_ID:
                    bot.send_message(CHAT_ID, msg)
                    print("Sent message to Telegram")

                if len(seen_signatures) > 10000:
                    seen_signatures.clear()

                await asyncio.sleep(1)
            except Exception as e:
                print("Error parsing message:", e)

if __name__ == "__main__":
    print("Starting bot...")
    asyncio.run(pumpfun_listener())
