#!/bin/bash
# post_deploy.sh — Run after each file sync to apply changes
# Usage: bash post_deploy.sh
set -e

PROJECT_DIR="/home/dphoompat/peyo-agent"

echo "[post-deploy] Activating venv..."
cd "$PROJECT_DIR"
source venv/bin/activate

echo "[post-deploy] Installing/updating dependencies..."
pip install -r requirements.txt -q

echo "[post-deploy] Running migrations..."
python manage.py migrate --noinput

echo "[post-deploy] Collecting static files..."
python manage.py collectstatic --noinput -v 0

deactivate

echo "[post-deploy] Restarting Gunicorn..."
sudo systemctl restart peyo-agent

echo "[post-deploy] Done. Site running at http://192.168.1.203"
