# -*- coding: utf-8 -*-
r"""ลิสต์ user ที่เข้าหลังบ้านได้ (staff/superuser) — แสดงเฉพาะ username ไม่มีรหัสผ่าน"""
import os, sys, django

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_automate.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

print("DB engine :", settings.DATABASES["default"]["ENGINE"])
print("DB name   :", settings.DATABASES["default"]["NAME"])
print()
print("%-22s %-30s %-6s %-6s %-8s %s" % ("USERNAME", "EMAIL", "STAFF", "SUPER", "ACTIVE", "LAST LOGIN"))
print("-" * 100)
for u in User.objects.filter(is_staff=True).order_by("-is_superuser", "username"):
    print("%-22s %-30s %-6s %-6s %-8s %s" % (
        u.username,
        u.email or "-",
        "yes" if u.is_staff else "-",
        "yes" if u.is_superuser else "-",
        "yes" if u.is_active else "NO",
        u.last_login.strftime("%Y-%m-%d %H:%M") if u.last_login else "ยังไม่เคย login",
    ))

print()
print("staff ทั้งหมด :", User.objects.filter(is_staff=True).count(),
      "| superuser :", User.objects.filter(is_superuser=True).count(),
      "| user ทั้งหมด :", User.objects.count())
