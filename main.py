import os
import telebot
import websocket
import threading
import json
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)  # disable internal threading to avoid conflict

def on_open(ws):
    print("WebSocket connection opened")
    ws.send(json.dumps({"method": "subscribeNewToken"}))

def on_message(ws, message):
    print("New token payload:", message)
    data = json.loads(message)
    token_info = data.get("data", {})
    token_name = token_info.get("tokenName", "Unknown")
    token_address = token_info.get("mintAddress", "")
    liquidity = token_info.get("liquidity", 0)

    msg = f"👀 New Token Launched!\nName: {token_name}\nAddress: {token_address}\nLiquidity: {liquidity}"
    print(msg)
    if CHAT_ID:
        bot.send_message(CHAT_ID, msg)

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
    bot.infinity_polling()
