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

alerted_bonded = set()

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
                event_type = data.get('method', '')

                if event_type != 'subscribeMigration':
                    continue

                print("DEBUG migration event:")
                print(json.dumps(data, indent=2))

                token_address = data.get('mint', '').strip().lower()
                if not token_address or token_address in alerted_bonded:
                    continue

                migration_type = data.get('migrationType', '').lower()
                if migration_type != 'bonding':
                    continue

                alerted_bonded.add(token_address)
                token_name = data.get('name', 'Unknown')
                dexscreener_link = f"https://dexscreener.com/solana/{token_address}"
                image_url = data.get('image', '')

                caption = (
                    f"🔥 New token just bonded on pump.fun!\n"
                    f"Name: {token_name}\n"
                    f"Address: {token_address}\n"
                    f"[View on Dexscreener]({dexscreener_link})"
                )

                if image_url:
                    bot.send_photo(CHAT_ID, image_url, caption=caption, parse_mode="Markdown")
                else:
                    bot.send_message(CHAT_ID, caption, parse_mode="Markdown")

                print("Sent bonded alert to Telegram")

            except Exception as e:
                print("Error parsing message:", e)

if __name__ == "__main__":
    print("Starting bot...")
    asyncio.run(pumpfun_listener())
