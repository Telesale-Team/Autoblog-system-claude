# -*- coding: utf-8 -*-
"""
สร้าง/รีเซ็ต demo account สำหรับ prospect บน noodee-booking (เว็บ demo QueueFlow)

รันบน server 192.168.1.2:
    ssh -i ~/.ssh/id_ubuntu_local dphoompat@192.168.1.2 \
        "/home/dphoompat/noodee-booking/venv/bin/python -" < scripts/noodee_demo_account.py

ทำอะไร:
- สร้าง (หรือรีเซ็ต) user `demo_owner` role=owner สำหรับให้ prospect login ดู dashboard เจ้าของ
- ไม่ให้สิทธิ์ Django admin (is_staff=False, is_superuser=False)
- ตั้งใจให้รันซ้ำได้เรื่อยๆ (idempotent) — ใช้เป็น reset script รายวัน/รายสัปดาห์ผ่าน cron ได้:
    0 4 * * * /home/dphoompat/noodee-booking/venv/bin/python /home/dphoompat/noodee-booking/scripts/noodee_demo_account.py

Credential ที่แจก prospect (แปะใน sale kit / LINE):
    URL:      https://booking.noodee-bootbiz.com/login/
    Username: demo_owner
    Password: NoodeeDemo2026
"""
import os
import sys

BASE = "/home/dphoompat/noodee-booking"
sys.path.insert(0, BASE)
os.chdir(BASE)
for line in open(f"{BASE}/.env"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())
os.environ["DJANGO_SETTINGS_MODULE"] = "skin_settings_production"

import django

django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

u, created = User.objects.get_or_create(
    username="demo_owner",
    defaults={"email": "demo@noodee-bootbiz.com", "first_name": "Demo", "last_name": "Owner"},
)
u.set_password("NoodeeDemo2026")
u.role = "owner"
u.is_staff = False       # ห้ามเข้า Django admin
u.is_superuser = False
u.is_active = True
u.save()
print(("created" if created else "reset"), "-> demo_owner (role=owner)")
