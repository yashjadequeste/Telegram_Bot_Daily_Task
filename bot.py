import os
import uuid
from datetime import time

import pytz
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from tenacity import retry, stop_after_attempt

from ai_formatter import format_task, parse_ai_response
from email_sender import send_email
from excel_handler import WORKBOOK_PATH, update_excel
from task_manager import (
    ACTIVE_STATUSES,
    add_task,
    change_task_status,
    complete_tasks_by_ids,
    get_pending_tasks,
    get_task_by_id,
)
from work_calendar import ALLOW_WEEKEND_TEST, is_working_day

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
REMINDER_HOUR = int(os.getenv("REMINDER_HOUR", "19"))
REMINDER_MINUTE = int(os.getenv("REMINDER_MINUTE", "0"))
SEND_TEST_ON_START = os.getenv("SEND_TEST_ON_START", "false").lower() in (
    "1", "true", "yes", "on"
)

STATUS_ICONS = {
    "Completed": "✅",
    "In Progress": "⏳",
    "Pending": "❌",
}


def status_keyboard(prefix):
    return [
        [
            InlineKeyboardButton("✅ Completed", callback_data=f"{prefix}|Completed"),
            InlineKeyboardButton("⏳ In Progress", callback_data=f"{prefix}|In Progress"),
            InlineKeyboardButton("❌ Pending", callback_data=f"{prefix}|Pending"),
        ]
    ]


async def send_daily_reminder(context, force=False):
    try:
        if not force and not is_working_day():
            print("Skip reminder — weekend (set ALLOW_WEEKEND_TEST=true).")
            return

        chat_id = CHAT_ID or os.getenv("TELEGRAM_CHAT_ID")
        if not chat_id:
            print("ERROR: TELEGRAM_CHAT_ID not set in Railway Variables!")
            return

        await context.bot.send_message(
            chat_id=int(chat_id),
            text=(
                "🔔 *Daily Report Reminder*\n\n"
                "Tap *Start Daily Report* below:\n"
                "1️⃣ Complete pending tasks\n"
                "2️⃣ Add today's task\n"
                "3️⃣ Send email with Excel"
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("▶️ Start Daily Report", callback_data="evening|begin")]
            ]),
            parse_mode="Markdown",
            disable_notification=False,
        )
        print(f"Reminder sent to chat_id={chat_id}")
    except Exception as e:
        print(f"REMINDER FAILED: {e}")


async def _test_reminder_on_start(context):
    await send_daily_reminder(context, force=True)


def setup_reminder_jobs(app):
    ist = pytz.timezone("Asia/Kolkata")
    reminder_time = time(
        hour=REMINDER_HOUR,
        minute=REMINDER_MINUTE,
        tzinfo=ist,
    )

    if ALLOW_WEEKEND_TEST:
        days = (0, 1, 2, 3, 4, 5, 6)
    else:
        days = (0, 1, 2, 3, 4)

    app.job_queue.run_daily(
        send_daily_reminder,
        time=reminder_time,
        days=days,
        name="daily_reminder",
    )

    print(
        f"Reminder scheduled {REMINDER_HOUR:02d}:{REMINDER_MINUTE:02d} IST | "
        f"days={days} | ALLOW_WEEKEND_TEST={ALLOW_WEEKEND_TEST} | CHAT_ID={CHAT_ID}"
    )

    if SEND_TEST_ON_START:
        app.job_queue.run_once(_test_reminder_on_start, when=15, name="test_on_start")
        print("Test notification in 15 seconds (SEND_TEST_ON_START=true)")


async def cmd_testnotif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_daily_reminder(context, force=True)
    await update.message.reply_text("Test notification sent! Check Telegram.")


def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ Start 7 PM Report", callback_data="evening|begin")],
        [InlineKeyboardButton("➕ Add Task (Excel only)", callback_data="menu|add")],
        [InlineKeyboardButton("📋 Manage Pending (Excel only)", callback_data="menu|manage")],
        [InlineKeyboardButton("❓ Help", callback_data="menu|help")],
    ])


def evening_select_keyboard(selected_ids):
    pending = get_pending_tasks()
    rows = []

    for task in pending:
        checked = "✅" if task["id"] in selected_ids else "⬜"
        label = f"{checked} {task['task_type'][:38]}"
        rows.append([
            InlineKeyboardButton(label, callback_data=f"evening|toggle|{task['id']}")
        ])

    rows.append([
        InlineKeyboardButton("✔️ Done → Next", callback_data="evening|confirm"),
        InlineKeyboardButton("⏭ Skip", callback_data="evening|skip"),
    ])
    return InlineKeyboardMarkup(rows)


def help_text():
    return (
        "🤖 *Daily Report Bot*\n\n"
        "*7 PM flow (1 email per day)*\n"
        "1️⃣ Select pending tasks → mark Completed\n"
        "2️⃣ Pick today's status\n"
        "3️⃣ Write your task → AI formats → Excel\n"
        "4️⃣ Email sent once with sheet + signature\n\n"
        "*During day*\n"
        "• Manage pending → Excel only, no email\n"
        "• Add task → Excel only, no email\n\n"
        "/evening — start 7 PM flow anytime (test)\n"
        "/menu — main menu"
    )


async def start_evening_flow(query, context):
    context.user_data["flow"] = "evening_select"
    context.user_data["selected"] = []

    pending = get_pending_tasks()
    if pending:
        text = (
            "🔔 *Daily Report — Step 1*\n\n"
            "Select pending tasks to mark *Completed*.\n"
            "Tap tasks to select/deselect (multiple OK).\n"
            "Then tap *Done → Next*."
        )
        await query.edit_message_text(
            text,
            reply_markup=evening_select_keyboard([]),
            parse_mode="Markdown",
        )
    else:
        await ask_evening_status(query, context)


async def ask_evening_status(query, context):
    context.user_data["flow"] = "evening_status"
    await query.edit_message_text(
        "📝 *Step 2 — Today's task status*\n\nSelect status:",
        reply_markup=InlineKeyboardMarkup(status_keyboard("evening")),
        parse_mode="Markdown",
    )


async def ask_evening_task_text(query, context, status):
    context.user_data["flow"] = "evening_task"
    context.user_data["evening_status"] = status
    await query.edit_message_text(
        f"📝 *Step 3 — Today's work*\n\n"
        f"Status: `{status}`\n\n"
        f"Now send your full task notes in one message "
        f"(AI will format and add to Excel, then email will be sent once).",
        parse_mode="Markdown",
    )


@retry(stop=stop_after_attempt(3))
def process_report(task, status, track_pending=True):
    ai_response = format_task(task)
    task_type, professional_update = parse_ai_response(ai_response)
    excel_path, row = update_excel(professional_update, task_type, status)

    if track_pending and status in ACTIVE_STATUSES:
        add_task({
            "id": str(uuid.uuid4()),
            "task_type": task_type,
            "status": status,
            "row": row,
        })

    return excel_path, task_type, status


async def send_main_menu(update, text="📌 Main Menu"):
    await update.message.reply_text(
        text,
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown",
    )


async def send_manage_tasks(target, edit=False):
    pending = get_pending_tasks()

    if not pending:
        text = "No Pending / In Progress tasks."
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Menu", callback_data="menu|home")]
        ])
    else:
        text = "📋 *Tap task to change status* (Excel only, no email):\n\n"
        rows = []
        for task in pending:
            icon = STATUS_ICONS.get(task["status"], "•")
            text += f"{icon} {task['task_type']} — `{task['status']}`\n"
            rows.append([
                InlineKeyboardButton(
                    f"{icon} {task['task_type'][:35]}",
                    callback_data=f"pick|{task['id']}",
                )
            ])
        rows.append([InlineKeyboardButton("⬅️ Menu", callback_data="menu|home")])
        keyboard = InlineKeyboardMarkup(rows)

    if edit:
        await target.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        msg = target.message if hasattr(target, "message") else target
        await msg.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not is_working_day():
        await update.message.reply_text(
            f"Holiday (Sat/Sun). ALLOW_WEEKEND_TEST=true for testing.\n\n"
            f"Your Chat ID for `.env`:\n`TELEGRAM_CHAT_ID={chat_id}`",
            parse_mode="Markdown",
        )
        return

    await update.message.reply_text(
        f"Your Chat ID (put in `.env`):\n`TELEGRAM_CHAT_ID={chat_id}`",
        parse_mode="Markdown",
    )
    await send_main_menu(update)


async def cmd_myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"Your Telegram Chat ID:\n\n`TELEGRAM_CHAT_ID={chat_id}`\n\n"
        f"Copy this into `.env` then restart scheduler.",
        parse_mode="Markdown",
    )


async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_main_menu(update)


async def cmd_evening(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["flow"] = "evening_select"
    context.user_data["selected"] = []
    pending = get_pending_tasks()

    if pending:
        await update.message.reply_text(
            "🔔 *Daily Report — Step 1*\n\nSelect pending tasks (tap to toggle):",
            reply_markup=evening_select_keyboard([]),
            parse_mode="Markdown",
        )
    else:
        context.user_data["flow"] = "evening_status"
        await update.message.reply_text(
            "📝 *Step 2 — Today's status:*",
            reply_markup=InlineKeyboardMarkup(status_keyboard("evening")),
            parse_mode="Markdown",
        )


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # ---- 7 PM evening flow ----
    if data == "evening|begin":
        await start_evening_flow(query, context)
        return

    if data.startswith("evening|toggle|"):
        task_id = data.split("|", 2)[2]
        selected = set(context.user_data.get("selected", []))
        if task_id in selected:
            selected.discard(task_id)
        else:
            selected.add(task_id)
        context.user_data["selected"] = list(selected)
        await query.edit_message_reply_markup(
            reply_markup=evening_select_keyboard(selected)
        )
        return

    if data in ("evening|confirm", "evening|skip"):
        if data == "evening|confirm":
            ids = context.user_data.get("selected", [])
            if ids:
                complete_tasks_by_ids(ids)
        await ask_evening_status(query, context)
        return

    if data.startswith("evening|"):
        status = data.split("|", 1)[1]
        if status in ("Completed", "In Progress", "Pending"):
            await ask_evening_task_text(query, context, status)
        return

    # ---- Main menu ----
    if data.startswith("menu|"):
        action = data.split("|", 1)[1]

        if action == "home":
            context.user_data.clear()
            await query.edit_message_text(
                "📌 Main Menu",
                reply_markup=main_menu_keyboard(),
            )
            return

        if action == "add":
            context.user_data["flow"] = "manual_status"
            await query.edit_message_text(
                "Select status (Excel only, no email):",
                reply_markup=InlineKeyboardMarkup(status_keyboard("new")),
            )
            return

        if action == "manage":
            await send_manage_tasks(query, edit=True)
            return

        if action == "help":
            await query.edit_message_text(
                help_text(),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Menu", callback_data="menu|home")]
                ]),
                parse_mode="Markdown",
            )
            return

    # ---- Manual new task status ----
    if data.startswith("new|"):
        status = data.split("|", 1)[1]
        context.user_data["flow"] = "manual_task"
        context.user_data["manual_status"] = status
        await query.edit_message_text(
            f"Status: `{status}`\n\nSend work notes (Excel only, no email):",
            parse_mode="Markdown",
        )
        return

    # ---- Manage single task ----
    if data.startswith("pick|"):
        task_id = data.split("|", 1)[1]
        task = get_task_by_id(task_id)
        if not task:
            await query.edit_message_text("Task not found.")
            return
        keyboard = InlineKeyboardMarkup(
            status_keyboard(f"set|{task_id}")
            + [[InlineKeyboardButton("⬅️ Back", callback_data="menu|manage")]]
        )
        await query.edit_message_text(
            f"*{task['task_type']}*\nStatus: `{task['status']}`\n\nSelect new status (Excel only):",
            reply_markup=keyboard,
            parse_mode="Markdown",
        )
        return

    if data.startswith("set|"):
        parts = data.split("|")
        if len(parts) != 3:
            return
        _, task_id, new_status = parts
        task = get_task_by_id(task_id)
        if not task:
            await query.edit_message_text("Task not found.")
            return

        change_task_status(task_id, new_status)
        icon = STATUS_ICONS.get(new_status, "•")
        await query.edit_message_text(
            f"{icon} *{task['task_type']}*\n"
            f"`{task['status']}` → `{new_status}`\n"
            f"Excel updated ✅ (no email)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 More", callback_data="menu|manage")],
                [InlineKeyboardButton("⬅️ Menu", callback_data="menu|home")],
            ]),
            parse_mode="Markdown",
        )
        return


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not is_working_day():
            await update.message.reply_text("Holiday. ALLOW_WEEKEND_TEST=true to test.")
            return

        text = update.message.text.strip()
        if not text:
            await update.message.reply_text("Please send your task text.")
            return

        flow = context.user_data.get("flow")

        # 7 PM flow — send email once
        if flow == "evening_task":
            status = context.user_data.get("evening_status", "Completed")
            process_report(text, status, track_pending=True)
            send_email(str(WORKBOOK_PATH))
            context.user_data.clear()
            await update.message.reply_text(
                f"✅ *Done!*\n\n"
                f"• Pending tasks updated in Excel\n"
                f"• Today's task added (`{status}`)\n"
                f"• *One email sent* with Excel + signature",
                reply_markup=main_menu_keyboard(),
                parse_mode="Markdown",
            )
            return

        # Manual add — Excel only
        if flow == "manual_task":
            status = context.user_data.get("manual_status", "Completed")
            _, task_type, _ = process_report(text, status, track_pending=True)
            context.user_data.clear()
            await update.message.reply_text(
                f"✅ Excel updated: *{task_type}* (`{status}`)\nNo email (email only at 7 PM flow).",
                reply_markup=main_menu_keyboard(),
                parse_mode="Markdown",
            )
            return

        await update.message.reply_text(
            "Use /menu or tap *Start 7 PM Report* for daily flow.",
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", cmd_menu))
    app.add_handler(CommandHandler("evening", cmd_evening))
    app.add_handler(CommandHandler("myid", cmd_myid))
    app.add_handler(CommandHandler("testnotif", cmd_testnotif))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    setup_reminder_jobs(app)

    print("Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
