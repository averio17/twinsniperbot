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
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"method": "subscribeNewToken"}))
        await ws.send(json.dumps({"method": "subscribeMigration"}))

        async for message in ws:
            try:
                data = json.loads(message)
                print(json.dumps(data, indent=2))  # Print the full payload

                token_name = data.get('name', 'Unknown')
                token_address = data.get('mint', 'Unknown')
                liquidity = data.get('marketCapSol', 'Not provided')

                msg = f"🔥 New token launched!\nName: {token_name}\nAddress: {token_address}\nMarket Cap (SOL): {liquidity}"
                if CHAT_ID:
                    bot.send_message(CHAT_ID, msg)
            except Exception as e:
                print("Error parsing message:", e)

if __name__ == "__main__":
    asyncio.run(pumpfun_listener())
