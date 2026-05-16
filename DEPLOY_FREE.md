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

Oracle આપે છે **forever free** small server (VM).

### Steps

1. [cloud.oracle.com](https://cloud.oracle.com) → Sign up (card verify, charge નહીં free tier માટે)
2. **Create VM** → Ubuntu 22.04 → **Always Free** shape (ARM Ampere 4 OCPU / 24 GB RAM)
3. SSH connect:
   ```bash
   ssh ubuntu@YOUR_VM_IP
   ```
4. Install:
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip git
   git clone https://github.com/YOUR_USER/daily-report-bot.git
   cd daily-report-bot
   pip3 install -r requirements.txt
   ```
5. Create `.env` on server (copy from your local, **do not push to GitHub**):
   ```bash
   nano .env
   ```
6. Run always (systemd):
   ```bash
   sudo nano /etc/systemd/system/daily-report.service
   ```
   Paste:
   ```ini
   [Unit]
   Description=Daily Report Telegram Bot
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/daily-report-bot
   ExecStart=/usr/bin/python3 app.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```
   ```bash
   sudo systemctl enable daily-report
   sudo systemctl start daily-report
   sudo systemctl status daily-report
   ```
7. Reports save at: `/home/ubuntu/daily-report-bot/reports/`

**Cost: ₹0/month** (always free tier limits અંદર)

---

## Option 3 — Fly.io (Free allowance)

1. [fly.io](https://fly.io) → sign up
2. Install flyctl → `fly launch` in project folder
3. Set secrets: `fly secrets set TELEGRAM_BOT_TOKEN=...` (all env vars)
4. Deploy: `fly deploy`
5. Add **volume** for `reports/` folder (important for Excel save)

Free tier limited hours/credit — check fly.io pricing page.

---

## Option 4 — Render Free Web (NOT recommended for this bot)

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
