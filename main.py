import json
import threading
import websocket
from dotenv import load_dotenv
import os
from telebot import TeleBot

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = TeleBot(BOT_TOKEN)

def on_open(ws):
    print("WebSocket connection opened")
    ws.send(json.dumps({"method": "subscribeNewToken"}))

def on_message(ws, message):
    print("Raw payload:", message)
    try:
        data = json.loads(message)
        token_info = data.get("data", {})

        token_name = token_info.get("tokenName") or token_info.get("name", "Unknown")
        token_address = token_info.get("mintAddress", "")
        liquidity = token_info.get("liquidity")

        if liquidity is None:
            liquidity = "Not provided"

        msg = f"👀 New Token Launched!\nName: {token_name}\nAddress: {token_address}\nLiquidity: {liquidity}"

        if CHAT_ID:
            bot.send_message(CHAT_ID, msg)

    except Exception as e:
        print("Error parsing message:", e)

def on_error(ws, error):
    print("WebSocket error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")

def run_websocket():
    ws = websocket.WebSocketApp(
        "wss://pumpportal.fun/api/data",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

if __name__ == "__main__":
    threading.Thread(target=run_websocket, daemon=True).start()
    print("Bot is running and listening for new token launches...")
    while True:
        pass
