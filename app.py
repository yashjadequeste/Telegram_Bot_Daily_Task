"""
One command: bot + reminder scheduler (inside bot, Railway-safe).

    python app.py
"""
from dotenv import load_dotenv

load_dotenv()

from bot import main

if __name__ == "__main__":
    print("=" * 50)
    print("Daily Report Bot starting (bot + scheduler)...")
    print("=" * 50)
    main()
