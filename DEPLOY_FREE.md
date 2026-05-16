# Free Deploy Guide (Render Worker Paid છે)

Render **Background Worker = paid**. Free માટે નીચેના options.

---

## Reports ક્યાં save થાય?

| Location | Path |
|----------|------|
| **Your PC (local)** | `D:\my\daily-report-bot\reports\Daily_Report.xlsx` |
| **Cloud VPS (Oracle/Fly)** | `/home/you/daily-report-bot/reports/Daily_Report.xlsx` |
| **tasks.json** | `reports/tasks.json` |

Email પણ daily Excel attach કરીને receivers ને જાય છે — cloud પર file ખોવાય તો પણ email માં copy રહે.

---

## Option 1 — Local PC (100% FREE) ⭐ સૌથી સરળ

તમારો PC on હોય ત્યારે bot + 7 PM scheduler ચાલે.

```bash
cd D:\my\daily-report-bot
python app.py
```

- Reports: `reports\Daily_Report.xlsx`
- Cost: **₹0**
- Minus: PC બંધ = bot બંધ

**PC બંધ પછી પણ reminder:** Windows Task Scheduler થી startup પર `run.bat` ચલાવો.

---

## Option 2 — Oracle Cloud Always Free (24/7 FREE) ⭐ recommended

**Full step-by-step guide:** **[DEPLOY_ORACLE.md](DEPLOY_ORACLE.md)**

Quick summary:
1. [cloud.oracle.com](https://cloud.oracle.com) → sign up (card verify)
2. Create Ubuntu VM — **Ampere Always Free** shape
3. SSH → `git clone` your repo
4. `nano .env` → add secrets
5. `./deploy/setup-oracle.sh` → auto install + 24/7 service
6. Telegram `/testnotif` test

Reports: `/home/ubuntu/daily-report-bot/reports/`

---

## Option 3 — Railway (build fix applied)

Railway uses Python **3.13** by default — `Pillow==10.2.0` fails.

Project now has:
- `runtime.txt` → Python **3.10**
- `railway.toml` → `python app.py`
- `Pillow>=10.4.0`

**Railway setup:**
1. New Project → Deploy from GitHub repo
2. **Variables** → add all from `.env.example` (not `.env` file)
3. Deploy

**Note:** Railway free credit limited — not truly free 24/7 long term.

---

## Option 4 — Fly.io (Free allowance)

1. [fly.io](https://fly.io) → sign up
2. Install flyctl → `fly launch` in project folder
3. Set secrets: `fly secrets set TELEGRAM_BOT_TOKEN=...` (all env vars)
4. Deploy: `fly deploy`
5. Add **volume** for `reports/` folder (important for Excel save)

Free tier limited hours/credit — check fly.io pricing page.

---

## Option 5 — Render Free Web (NOT recommended for this bot)

Render **free web** sleeps after 15 min → Telegram bot + 7 PM scheduler **બરાબર કામ નહીં કરે**.

Worker જોઈએ = paid. એટલે Render free use ન કરો આ bot માટે.

---

## .env — ક્યાં set કરવું (free deploy)

| Deploy | .env location |
|--------|----------------|
| Local PC | `D:\my\daily-report-bot\.env` |
| Oracle VM | `/home/ubuntu/daily-report-bot/.env` |
| Fly.io | `fly secrets set KEY=value` |

**ક્યારેય GitHub પર .env push ન કરો.**

---

## Production settings (free 24/7)

```env
REMINDER_HOUR=19
REMINDER_MINUTE=0
ALLOW_WEEKEND_TEST=false
SEND_TEST_ON_START=false
EMAIL_RECEIVERS=email1@gmail.com,email2@gmail.com
```

---

## Quick choice

| તમને શું જોઈએ | Use |
|-------------|-----|
| સૌથી સરળ, PC on રાખી શકો | **Local `python app.py`** |
| 24/7, PC બંધ, completely free | **Oracle Cloud VM** |
| Test only | Local |

---

## Security reminder

તમે `.env` GitHub પર push કર્યું હતું → **બધા tokens rotate કરો** (BotFather, Groq, Gmail app password).
