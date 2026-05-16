#!/bin/bash
# Run on Oracle Cloud Ubuntu VM after cloning repo:
#   chmod +x deploy/setup-oracle.sh
#   ./deploy/setup-oracle.sh

set -e

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$APP_DIR"

echo "=== Daily Report Bot - Oracle setup ==="

sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

mkdir -p reports templates

if [ ! -f .env ]; then
  cp .env.example .env
  echo ""
  echo "IMPORTANT: Edit .env with your real keys:"
  echo "  nano .env"
  echo ""
fi

sudo cp deploy/daily-report.service /etc/systemd/system/daily-report.service
sudo sed -i "s|/home/ubuntu/daily-report-bot|$APP_DIR|g" /etc/systemd/system/daily-report.service
sudo systemctl daemon-reload
sudo systemctl enable daily-report
sudo systemctl restart daily-report

echo ""
echo "=== Done ==="
echo "Status:  sudo systemctl status daily-report"
echo "Logs:    sudo journalctl -u daily-report -f"
echo "Test:    send /testnotif to your Telegram bot"
