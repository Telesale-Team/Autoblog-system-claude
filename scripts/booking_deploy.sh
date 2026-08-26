#!/bin/bash
set -e
echo '>>> git pull'
git pull origin main
echo '>>> pip install'
source /home/dphoompat/booking-system/venv/bin/activate && pip install -r requirements.txt -q
echo '>>> migrate'
python manage.py migrate --noinput
echo '>>> collectstatic'
python manage.py collectstatic --noinput --clear -v 0
echo '>>> restart service'
sudo systemctl restart booking-system
echo '>>> done'
sudo systemctl is-active booking-system
