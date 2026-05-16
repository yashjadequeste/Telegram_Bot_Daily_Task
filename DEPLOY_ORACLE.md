# Oracle Cloud પર Deploy — Full Process

24/7 free bot + 7 PM reminder + Excel save.  
Card verify થાય (charge નહીં free tier માં).

---

## Part 1 — Oracle account + VM બનાવો

### Step 1: Sign up
1. [cloud.oracle.com](https://cloud.oracle.com) → **Sign Up**
2. Card details → verification (₹1 hold, refund)
3. Region select: **India West (Mumbai)** અથવા nearest

### Step 2: Create VM (Always Free)
1. Menu → **Compute** → **Instances** → **Create instance**
2. Name: `daily-report-bot`
3. **Image:** Ubuntu 22.04
4. **Shape:** Click **Change shape**
   - **Ampere** → `VM.Standard.A1.Flex`
   - 1 OCPU, 6 GB RAM (free માં પૂરતું)
5. **Networking:** Create new VCN (default OK)
6. **SSH keys:** Download private key OR paste your public key
7. Click **Create**

⏳ 2–3 minutes wait → **Public IP** copy કરો (દા.ત. `129.152.x.x`)

### Step 3: Firewall (SSH)
1. Instance → **Subnet** → **Security List**
2. **Ingress Rules** → Add:
   - Source: `0.0.0.0/0` (અથવા તમારો IP only)
   - Port: `22`
   - Protocol: TCP

---

## Part 2 — Server પર connect કરો

### Windows (PowerShell)
```powershell
ssh -i "C:\path\to\your-key.key" ubuntu@YOUR_PUBLIC_IP
```

પહેલી વાર:
```bash
sudo apt update
```

---

## Part 3 — Code install કરો

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/daily-report-bot.git
cd daily-report-bot
```

(તમારો GitHub repo URL નાખો)

---

## Part 4 — .env file બનાવો

```bash
nano .env
```

આ values નાખો (તમારા real values):

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=5090519670

GROQ_API_KEY=your_groq_key

EMAIL_SENDER=yash@jadequest.com
EMAIL_PASSWORD=your_gmail_app_password
EMAIL_RECEIVERS=email1@gmail.com,email2@gmail.com

REMINDER_HOUR=19
REMINDER_MINUTE=0

ALLOW_WEEKEND_TEST=false
SEND_TEST_ON_START=false
```

Save: `Ctrl+O` → Enter → `Ctrl+X`

---

## Part 5 — Auto setup script

```bash
chmod +x deploy/setup-oracle.sh
./deploy/setup-oracle.sh
```

આ script:
- Python venv બનાવે
- packages install કરે
- systemd service setup કરે (24/7 auto restart)

---

## Part 6 — Check કરો

```bash
sudo systemctl status daily-report
```

**Active (running)** દેખાવું જોઈએ.

Logs live:
```bash
sudo journalctl -u daily-report -f
```

આ lines જુઓ:
```
Reminder scheduled 19:00 IST
Telegram polling ready
Bot Running...
```

---

## Part 7 — Telegram test

Bot માં મોકલો:
```
/testnotif
/myid
/menu
```

Notification આવે = ✅ success

---

## Reports ક્યાં save થાય?

```
/home/ubuntu/daily-report-bot/reports/Daily_Report.xlsx
/home/ubuntu/daily-report-bot/reports/tasks.json
```

Download કરવા (local PC થી):
```powershell
scp -i "your-key.key" ubuntu@YOUR_IP:~/daily-report-bot/reports/Daily_Report.xlsx .
```

---

## Useful commands

| Command | શું કરે |
|---------|---------|
| `sudo systemctl restart daily-report` | Bot restart |
| `sudo systemctl stop daily-report` | Bot stop |
| `sudo journalctl -u daily-report -f` | Live logs |
| `cd ~/daily-report-bot && git pull` | Code update |
| `sudo systemctl restart daily-report` | Update પછી restart |

---

## Code update પછી

```bash
cd ~/daily-report-bot
git pull
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart daily-report
```

---

## Important rules

| Rule | Why |
|------|-----|
| **ફક્ત Oracle પર bot** | PC + Oracle બંને = Conflict error |
| `.env` GitHub પર નહીં | Secrets safe રાખો |
| `ALLOW_WEEKEND_TEST=false` | Production Mon–Fri |
| `REMINDER_HOUR=19` | 7 PM IST |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| SSH connect નહીં થાય | Security list port 22 open |
| Bot conflict error | PC પર bot બંધ કરો |
| No notification | `/testnotif` → logs check |
| Excel missing | `ls reports/` on server |

---

## Cost

**₹0/month** — Always Free tier (1 small VM)

⚠️ Paid service accidentally create ન કરો (Autonomous DB, Load Balancer, etc.)
