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

                # Subscribing to events
                await ws.send(json.dumps({"method": "subscribeNewToken"}))
                await ws.send(json.dumps({"method": "subscribeMigration"}))
                await ws.send(json.dumps({
                    "method": "subscribeAccountTrade",
                    "keys": ["AArPXm8JatJiuyEffuC1un2Sc835SULa4uQqDcaGpAjV"]
                }))
                await ws.send(json.dumps({
                    "method": "subscribeTokenTrade",
                    "keys": ["91WNez8D22NwBssQbkzjy4s2ipFrzpmn5hfvWVe2aY5p"]
                }))
                print("Subscribed to all events.")

                async for message in ws:
                    try:
                        data = json.loads(message)
                        print("DEBUG:", json.dumps(data, indent=2))

                        # Migration bonded event
                        migration_type = data.get("migrationType", "").lower()
                        token_address = data.get("mint", "").strip().lower()

                        if migration_type == "bonding" and token_address and token_address not in alerted_bonded:
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

                        # New token event
                        if data.get("method") == "newToken":
                            token_info = data.get("params", {})
                            token_name = token_info.get("name", "Unknown")
                            token_address = token_info.get("mint", "")
                            msg = (
                                f"🆕 *New Token Created!*\n\n"
                                f"*Name:* {token_name}\n"
                                f"*Address:* `{token_address}`"
                            )
                            bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
                            print("Sent new token alert to Telegram!")

                    except Exception as e:
                        print("Error parsing or sending alert:", e)

        except Exception as e:
            print("Connection error:", e)
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(pumpfun_listener())
