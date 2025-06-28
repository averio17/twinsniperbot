import os
import asyncio
import websockets
import json
from telebot import TeleBot

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = TeleBot(BOT_TOKEN)

alerted_bonded = set()

async def pumpfun_listener():
    while True:
        try:
            uri = "wss://pumpportal.fun/api/data"
            print("Connecting to websocket...")
            async with websockets.connect(uri) as ws:
                print("Connected!")
                await ws.send(json.dumps({"method": "subscribeMigration"}))
                print("Subscribed to migration events.")

                async for message in ws:
                    data = json.loads(message)
                    print("DEBUG FULL MESSAGE:", json.dumps(data, indent=2))

                    token_address = data.get("mint", "").strip().lower()
                    if not token_address or token_address in alerted_bonded:
                        continue

                    migration_type = data.get("migrationType", "").lower()
                    if migration_type != "bonding":
                        continue

                    alerted_bonded.add(token_address)
                    token_name = data.get("name", "Unknown")
                    dexscreener_link = f"https://dexscreener.com/solana/{token_address}"

                    msg = (
                        f"🚀 *New Token Just Bonded on pump.fun!*\n\n"
                        f"*Name:* {token_name}\n"
                        f"*Address:* `{token_address}`\n"
                        f"[View on Dexscreener]({dexscreener_link})"
                    )

                    bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
                    print("Sent bonded alert to Telegram!")

        except Exception as e:
            print("Error:", e)
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(pumpfun_listener())
