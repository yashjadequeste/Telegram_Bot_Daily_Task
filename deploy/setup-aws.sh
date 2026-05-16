#!/bin/bash
# Run on AWS EC2 Ubuntu after cloning repo:
#   chmod +x deploy/setup-aws.sh
#   ./deploy/setup-aws.sh

set -e

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$APP_DIR"

echo "=== Daily Report Bot - AWS EC2 setup ==="

sudo apt update -y
sudo apt install -y git

# Prefer Python 3.12 (stable). Ubuntu 3.14 can cause crashes.
if command -v python3.12 &>/dev/null; then
  PY=python3.12
else
  sudo apt install -y python3.12 python3.12-venv python3.12-dev || true
  PY=python3.12
fi

if ! command -v "$PY" &>/dev/null; then
  echo "ERROR: python3.12 is required (python3.14 breaks python-telegram-bot)."
  echo "Run: sudo apt install -y python3.12 python3.12-venv python3.12-dev"
  exit 1
fi

echo "Using Python: $($PY --version)"

rm -rf .venv
$PY -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

mkdir -p reports templates

if [ ! -f templates/"Daily Task.xlsx" ]; then
  echo "ERROR: templates/Daily Task.xlsx missing! Upload template file."
  exit 1
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Edit .env then run: sudo systemctl restart daily-report"
  nano .env
fi

# Test run (shows real error if any)
echo "Testing bot start..."
timeout 8 python app.py || true

sudo cp deploy/daily-report.service /etc/systemd/system/daily-report.service
sudo sed -i "s|/home/ubuntu/Telegram_Bot_Daily_Task|$APP_DIR|g" /etc/systemd/system/daily-report.service
sudo systemctl daemon-reload
sudo systemctl enable daily-report
sudo systemctl restart daily-report

sleep 3
sudo systemctl status daily-report --no-pager || true

echo ""
echo "=== Done ==="
echo "Logs:    sudo journalctl -u daily-report -n 30 --no-pager"
echo "Test:    send /testnotif to your Telegram bot"
