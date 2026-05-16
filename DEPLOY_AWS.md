# AWS EC2 પર Deploy — Full Step-by-Step

તમારો bot 24/7 ચાલશે: Telegram + 7 PM reminder + Excel + Email.

**Cost (અંદાજ):**
- પહેલા **12 મહિના:** t3.micro free tier → લગભગ **₹0**
- પછી: ~**$7–10/month** અથવા **$200 credit** થી ~**20+ મહિના**

---

## પહેલાં — આ બંધ કરો

| બંધ કરો | કારણ |
|---------|------|
| PC પર `python app.py` / `run.bat` | Conflict error |
| Railway પર same bot | Conflict error |

**ફક્ત AWS પર એક જ bot ચાલે.**

---

## Part 1 — AWS Account

1. [aws.amazon.com](https://aws.amazon.com) → **Create an AWS Account**
2. Email, password, card verify
3. Plan: **Free** / Pay-as-you-go
4. Login → **AWS Management Console**

---

## Part 2 — EC2 Server બનાવો

### Step 1: Region
- ઉપર જમણી બાજુ region: **Asia Pacific (Mumbai) ap-south-1**

### Step 2: Launch instance
1. Search → **EC2** → **Launch instance**
2. **Name:** `daily-report-bot`
3. **AMI:** **Ubuntu Server 22.04 LTS** (Free tier eligible)
4. **Instance type:** `t3.micro` (Free tier eligible) ✅
5. **Key pair:** Create new → name `daily-report-key` → **Download .pem** file  
   Save: `C:\Users\YASH\Downloads\daily-report-key.pem`
6. **Network settings** → Edit:
   - ✅ Allow **SSH** traffic (port 22)
   - Source: **My IP** (સુરક્ષા માટે) અથવા Anywhere test માટે
7. **Storage:** 20–30 GB (free tier માં 30 GB OK)
8. **Launch instance**

⏳ 1–2 min → instance **Running**

### Step 3: Public IP
1. EC2 → **Instances** → તમારી instance select
2. **Public IPv4 address** copy કરો (દા.ત. `3.110.x.x`)

---

## Part 3 — Windows થી Connect (SSH)

### WSL (recommended on Windows):
```bash
cp /mnt/d/my/daily-report-bot/bot.pem ~/bot.pem
chmod 400 ~/bot.pem
ssh -i ~/bot.pem ubuntu@YOUR_PUBLIC_IP
```

### PowerShell (Windows):
```powershell
cd C:\Users\YASH\Downloads
icacls daily-report-key.pem /inheritance:r
icacls daily-report-key.pem /grant:r "%USERNAME%:R"
ssh -i "daily-report-key.pem" ubuntu@YOUR_PUBLIC_IP
```

`YOUR_PUBLIC_IP` ની જગ્યાએ EC2 IP નાખો. પહેલી વાર `yes` લખો.

> WSL error `Permissions 0777 too open` → key ને `~/bot.pem` પર copy કરી `chmod 400` કરો.

---

## Part 4 — Server પર Code Install

```bash
sudo apt update -y
sudo apt install -y git

cd ~
git clone https://github.com/YOUR_GITHUB_USERNAME/daily-report-bot.git
cd daily-report-bot
```

👉 તમારો real GitHub repo URL નાખો.

---

## Part 5 — .env File (Secrets)

```bash
nano .env
```

આ paste કરીને **તમારી values** નાખો:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_CHAT_ID=5090519670

GROQ_API_KEY=your_groq_api_key

EMAIL_SENDER=yash@jadequest.com
EMAIL_PASSWORD=your_gmail_app_password
EMAIL_RECEIVERS=email1@gmail.com,email2@gmail.com

REMINDER_HOUR=19
REMINDER_MINUTE=0

ALLOW_WEEKEND_TEST=false
SEND_TEST_ON_START=false
```

**Save:** `Ctrl+O` → Enter → `Ctrl+X`

> Gmail password = **App Password** (normal password નહીં)

---

## Part 6 — Auto Setup (Bot 24/7)

```bash
chmod +x deploy/setup-aws.sh
./deploy/setup-aws.sh
```

આ કરે છે:
- Python + packages install
- Bot **systemd service** (restart auto, 24/7)

### Check status:
```bash
sudo systemctl status daily-report
```

**active (running)** ✅

### Live logs:
```bash
sudo journalctl -u daily-report -f
```

આ દેખાવું જોઈએ:
```
Reminder scheduled 19:00 IST
Telegram polling ready
Bot Running...
```

`Ctrl+C` થી logs બંધ (bot ચાલુ રહેશે)

---

## Part 7 — Telegram Test

તમારા bot માં મોકલો:

```
/testnotif
```

→ Notification આવે ✅

```
/menu
/start
```

---

## Reports ક્યાં save થાય?

Server પર:
```
/home/ubuntu/daily-report-bot/reports/Daily_Report.xlsx
/home/ubuntu/daily-report-bot/reports/tasks.json
```

### PC પર download કરવા:
```powershell
scp -i "C:\Users\YASH\Downloads\daily-report-key.pem" ubuntu@YOUR_PUBLIC_IP:~/daily-report-bot/reports/Daily_Report.xlsx .
```

---

## Part 8 — Billing / Credit safe રાખવા

1. AWS Console → **Billing** → **Free Tier** જુઓ
2. **Budgets** → Create budget → $5 alert (optional)
3. ફક્ત **1 × t3.micro** રાખો — RDS, Load Balancer ન બનાવો
4. Instance બંધ ન કરો તો bot બંધ — **Running** રાખો

**$200 credit:** લગભગ **20–28 મહિના** (ફક્ત આ bot માટે)

---

## Code Update (પછી)

```bash
cd ~/daily-report-bot
git pull
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart daily-report
```

---

## Useful Commands

| Command | શું કરે |
|---------|---------|
| `sudo systemctl status daily-report` | Status |
| `sudo systemctl restart daily-report` | Restart |
| `sudo systemctl stop daily-report` | Stop |
| `sudo journalctl -u daily-report -f` | Live logs |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `AttributeError: _Updater__polling_cleanup_cb` | **Python 3.14 + PTB 20.7** — `pip install -r requirements.txt` (PTB 22+) |
| SSH નહીં થાય | Security group port 22, correct .pem path |
| `Conflict getUpdates` | PC/Railway bot બંધ કરો |
| `git pull` blocks on `setup-aws.sh` | `git stash` અથવા `git checkout -- deploy/setup-aws.sh` પછી pull |
| No notification | `/testnotif` + logs check |
| `TELEGRAM_CHAT_ID` error | `/myid` in bot, numeric ID in .env |
| Email fail | Gmail App Password use કરો |

### Python 3.14 crash (telegram `Updater` error)

Ubuntu 26 default = **Python 3.14**. `python3.12` apt માં નથી. Fix: **upgrade** `python-telegram-bot` to 22+ (already in `requirements.txt`).

```bash
cd ~/Telegram_Bot_Daily_Task
sudo systemctl stop daily-report
git pull
source .venv/bin/activate
pip install -r requirements.txt
python app.py      # "Bot Running..." — Ctrl+C
sudo systemctl restart daily-report
sudo systemctl status daily-report
```

જો `git pull` fail (local changes): `git stash` પછી pull.

**નવી EC2 instance:** Ubuntu **22.04 LTS** AMI use કરો (python3.12 apt માં મળે).

---

## Checklist ✅

- [ ] AWS EC2 t3.micro Ubuntu running
- [ ] `.env` server પર set (GitHub પર નહીં)
- [ ] `./deploy/setup-aws.sh` success
- [ ] `systemctl status` = active
- [ ] `/testnotif` works
- [ ] PC/Railway bot stopped
- [ ] `REMINDER_HOUR=19` production time

---

**તૈયાર!** Bot AWS પર 24/7 ચાલશે. 🎉
