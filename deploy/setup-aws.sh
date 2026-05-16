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

# Ubuntu 26 has only python3.14 in apt — use it with PTB 22+ (see requirements.txt).
# Ubuntu 22.04/24.04: python3.12 from apt also works.
PY=python3
if command -v python3.12 &>/dev/null; then
  PY=python3.12
elif ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 14) else 1)' 2>/dev/null; then
  PY=python3
else
  echo "Python 3.14 detected — installing python3.13 from deadsnakes (optional fallback)..."
  if ! command -v python3.13 &>/dev/null; then
    sudo apt install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt update -y
    sudo apt install -y python3.13 python3.13-venv python3.13-dev || true
  fi
  if command -v python3.13 &>/dev/null; then
    PY=python3.13
  fi
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
