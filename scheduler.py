import asyncio
import os

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

from work_calendar import ALLOW_WEEKEND_TEST, is_working_day

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
REMINDER_HOUR = int(os.getenv("REMINDER_HOUR", "19"))
REMINDER_MINUTE = int(os.getenv("REMINDER_MINUTE", "0"))
SEND_TEST_ON_START = os.getenv("SEND_TEST_ON_START", "false").lower() in (
    "1", "true", "yes", "on"
)

bot = Bot(token=BOT_TOKEN)


async def _send_reminder_async():
    await bot.send_message(
        chat_id=int(CHAT_ID),
        text=(
            "🔔 *Daily Report — 7:00 PM*\n\n"
            "Tap *Start Daily Report* below:\n"
            "1️⃣ Select pending → mark Completed\n"
            "2️⃣ Add today's task\n"
            "3️⃣ One email with Excel report"
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("▶️ Start Daily Report", callback_data="evening|begin")]
        ]),
        parse_mode="Markdown",
        disable_notification=False,
    )


def send_reminder():
    if not is_working_day():
        print("Skip reminder — weekend/holiday (Mon–Fri only).")
        return
    asyncio.run(_send_reminder_async())
    print("7 PM reminder sent.")


def start_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Kolkata")

    cron_days = "*" if ALLOW_WEEKEND_TEST else "mon-fri"

    scheduler.add_job(
        send_reminder,
        "cron",
        day_of_week=cron_days,
        hour=REMINDER_HOUR,
        minute=REMINDER_MINUTE,
        id="daily_reminder",
        replace_existing=True,
    )

    scheduler.start()
    print(
        f"Scheduler ON — {REMINDER_HOUR:02d}:{REMINDER_MINUTE:02d} IST, "
        f"Mon–Fri only, CHAT_ID={CHAT_ID}"
    )

    if SEND_TEST_ON_START:
        print("Test reminder on start...")
        send_reminder()


if __name__ == "__main__":
    import time
    start_scheduler()
    while True:
        time.sleep(3600)
