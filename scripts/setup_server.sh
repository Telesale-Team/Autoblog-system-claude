#!/bin/bash
# setup_server.sh — Run ONCE on Ubuntu server to install all dependencies
# Usage: bash setup_server.sh
set -e

PROJECT_DIR="/home/dphoompat/peyo-agent"
PYTHON_VERSION="3.12"

echo "========================================"
echo " Peyo Agent — Ubuntu Server Setup"
echo "========================================"

# ── 1. System update ──────────────────────────────────────────
echo "[1/8] Updating system packages..."
sudo apt-get update -qq
sudo apt-get upgrade -y -qq

# ── 2. Python 3.12 ───────────────────────────────────────────
echo "[2/8] Installing Python ${PYTHON_VERSION} via deadsnakes PPA..."
sudo apt-get install -y -qq software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update -qq
sudo apt-get install -y -qq \
    python3.12 python3.12-venv python3.12-dev \
    python3-pip build-essential \
    libmysqlclient-dev pkg-config \
    libjpeg-dev libpng-dev libwebp-dev \
    curl git unzip

# ── 3. Node.js 20 LTS ────────────────────────────────────────
echo "[3/8] Installing Node.js 20 LTS..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - -qq
sudo apt-get install -y -qq nodejs

# ── 4. Claude Code CLI ───────────────────────────────────────
echo "[4/8] Installing Claude Code CLI..."
sudo npm install -g @anthropic-ai/claude-code

# ── 5. Nginx ─────────────────────────────────────────────────
echo "[5/8] Installing Nginx..."
sudo apt-get install -y -qq nginx

# ── 6. Project virtual environment ───────────────────────────
echo "[6/8] Setting up Python virtual environment..."
cd "$PROJECT_DIR"
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install gunicorn -q
deactivate

# ── 7. Nginx config ──────────────────────────────────────────
echo "[7/8] Configuring Nginx..."
sudo tee /etc/nginx/sites-available/peyo-agent > /dev/null <<'NGINX'
server {
    listen 80;
    server_name 192.168.1.203 _;

    client_max_body_size 20M;

    location /static/ {
        alias /home/dphoompat/peyo-agent/staticfiles/;
    }

    location /media/ {
        alias /home/dphoompat/peyo-agent/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX

sudo ln -sf /etc/nginx/sites-available/peyo-agent /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# ── 8. Systemd service for Gunicorn ─────────────────────────
echo "[8/8] Creating Gunicorn systemd service..."
sudo tee /etc/systemd/system/peyo-agent.service > /dev/null <<SERVICE
[Unit]
Description=Peyo Agent — Django + Gunicorn
After=network.target

[Service]
User=dphoompat
Group=dphoompat
WorkingDirectory=/home/dphoompat/peyo-agent
EnvironmentFile=/home/dphoompat/peyo-agent/.env
ExecStart=/home/dphoompat/peyo-agent/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    --timeout 120 \
    AI_automate.wsgi:application
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE

sudo systemctl daemon-reload
sudo systemctl enable peyo-agent

echo ""
echo "========================================"
echo " Setup complete!"
echo " Next step: copy .env file, run migrations, then start service"
echo " See: scripts/post_deploy.sh"
echo "========================================"
