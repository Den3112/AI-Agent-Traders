#!/usr/bin/env python3
import os

import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def get_chat_id():
    if not TOKEN or ":" not in TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found or invalid in .env")
        return
        
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    print(f"Checking for messages at {url}...")
    print("TIP: Напишите любое сообщение вашему боту в Telegram сейчас, чтобы я мог увидеть ваш Chat ID.")
    
    try:
        response = requests.get(url).json()
        if response.get("ok") and response.get("result"):
            for update in response["result"]:
                chat_id = update.get("message", {}).get("chat", {}).get("id")
                user = update.get("message", {}).get("from", {}).get("username", "unknown")
                if chat_id:
                    print(f"FOUND: Chat ID = {chat_id} (User: @{user})")
                    return
            print("No messages found yet. Try again after sending a message.")
        else:
            print("No updates found. Make sure the bot is not used by another process and you've sent it a message.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_chat_id()
