"""Run this, then send /start to your bot in Telegram. Your chat ID will print."""
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TELEGRAM_BOT_TOKEN")

print("Open Telegram -> your bot -> send /start or /myid\nWaiting...\n")

seen = set()
for _ in range(60):
    r = requests.get(
        f"https://api.telegram.org/bot{token}/getUpdates",
        timeout=15,
    )
    for item in r.json().get("result", []):
        uid = item["update_id"]
        if uid in seen:
            continue
        seen.add(uid)

        msg = item.get("message") or item.get("callback_query", {}).get("message")
        if not msg:
            continue

        chat = msg["chat"]
        cid = chat["id"]
        name = chat.get("first_name", "")
        print(f"\n✅ Found! Add to .env:\nTELEGRAM_CHAT_ID={cid}\n({name})")
        print("\nThen run: python scheduler.py")
        raise SystemExit(0)

    time.sleep(2)

print("No message received. Send /start to the bot and run again.")
