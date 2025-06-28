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
        # Subscribe to new token events
        await ws.send(json.dumps({"method": "subscribeNewToken"}))
        # Subscribe to migration events
        await ws.send(json.dumps({"method": "subscribeMigration"}))

        async for message in ws:
            print("Raw payload:", message)
            try:
                data = json.loads(message)
                token_info = data.get('data', {})
                token_name = token_info.get('tokenName', 'Unknown')
                token_address = token_info.get('mintAddress', 'Unknown')
                liquidity = token_info.get('liquidity', 'Not provided')

                msg = f"🔥 New token launched!\nName: {token_name}\nAddress: {token_address}\nLiquidity: {liquidity}"
                if CHAT_ID:
                    bot.send_message(CHAT_ID, msg)
            except Exception as e:
                print("Error parsing message:", e)

if __name__ == "__main__":
    asyncio.run(pumpfun_listener())
