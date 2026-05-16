"""
Run bot + 7 PM scheduler together (one command).

Local:  python app.py
Render: startCommand in render.yaml
"""
import threading
import time

from dotenv import load_dotenv

load_dotenv()


def main():
    from scheduler import start_scheduler
    from bot import main as run_bot

    print("=" * 50)
    print("Daily Report Bot — starting...")
    print("  • Telegram bot (polling)")
    print("  • 7 PM reminder scheduler (Mon–Fri IST)")
    print("=" * 50)

    scheduler_thread = threading.Thread(
        target=start_scheduler,
        name="scheduler",
        daemon=True,
    )
    scheduler_thread.start()
    time.sleep(1)

    run_bot()


if __name__ == "__main__":
    main()
