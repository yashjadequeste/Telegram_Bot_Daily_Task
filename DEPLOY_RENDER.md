# Deploy Daily Report Bot on Render (Live)

## One command (local)

```bash
python app.py
```

Or double-click `run.bat` (Windows).

Runs **bot + 7 PM scheduler** together.

---

## Before Render deploy

1. Push code to **GitHub** (private repo recommended).
2. Telegram: get `TELEGRAM_CHAT_ID` via `/myid` in bot.
3. Gmail: use **App Password** (not normal password).
4. Copy `.env.example` → set values in Render dashboard.

---

## Render setup (step by step)

### 1. Create account
- Go to [render.com](https://render.com) → Sign up (GitHub login OK).

### 2. New Background Worker
- Dashboard → **New +** → **Background Worker**
- Connect your GitHub repo `daily-report-bot`
- Settings:
  - **Name:** `daily-report-bot`
  - **Runtime:** Python 3
  - **Build Command:** `pip install -r requirements.txt`
  - **Start Command:** `python app.py`
  - **Plan:** Free (or paid for 24/7 uptime)

### 3. Environment variables (Render → Environment)

| Key | Value |
|-----|--------|
| `TELEGRAM_BOT_TOKEN` | From @BotFather |
| `TELEGRAM_CHAT_ID` | Your numeric ID from `/myid` |
| `GROQ_API_KEY` | Groq API key |
| `EMAIL_SENDER` | yash@jadequest.com |
| `EMAIL_PASSWORD` | Gmail app password |
| `EMAIL_RECEIVERS` | `jatin@jadequest.com,other@mail.com` (comma separated) |
| `REMINDER_HOUR` | `19` |
| `REMINDER_MINUTE` | `0` |
| `ALLOW_WEEKEND_TEST` | `false` |
| `SEND_TEST_ON_START` | `false` |

### 4. Persistent disk (important)
- Worker → **Disks** → Add disk
- **Mount path:** `/opt/render/project/src/reports`
- **Size:** 1 GB  
Saves `Daily_Report.xlsx` and `tasks.json` after restart.

### 5. Deploy
- Click **Deploy** → wait for build green ✅
- Logs should show:
  ```
  Scheduler ON — 19:00 IST, Mon–Fri only
  Bot Running...
  ```

---

## Production rules (automatic)

| Rule | Behavior |
|------|----------|
| **7 PM reminder** | Mon–Fri only (IST) |
| **Weekend** | No reminder, bot says holiday |
| **Email** | Once per day after 7 PM flow |
| **Receivers** | All emails in `EMAIL_RECEIVERS` |

---

## Test on Render

1. Open Telegram → send `/menu` to your bot.
2. Tap **Start 7 PM Report** → complete flow.
3. Check receiver inbox(es) for Excel + signature.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| No 7 PM notification | Check logs; `TELEGRAM_CHAT_ID` must be numeric |
| Email fails | Gmail App Password; enable 2FA |
| Excel lost after restart | Add disk mount on `reports/` |
| Weekend test locally | `ALLOW_WEEKEND_TEST=true` in `.env` only |

---

## Update after code changes

Push to GitHub → Render auto-redeploys (if enabled) or manual **Deploy latest**.
