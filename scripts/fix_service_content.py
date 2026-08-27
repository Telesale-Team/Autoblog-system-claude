r"""ทำให้ข้อมูลบริการบนเว็บตรงกับของที่มีจริง — เฟส 9 กลุ่ม ก.

ที่มา: docs/review_products_sales_2026_08_27.md (Hustler) หัวข้อ 4
เจ้าของอนุมัติให้ลงมือ 27 ส.ค. 2569

สิ่งที่แก้ 5 เรื่อง:
  1. เปลี่ยนชื่อ "ระบบ Booking" -> "QueueFlow — ระบบจองคิวออนไลน์"
     prospect ที่ค้นเจอ QueueFlow แล้วมาเห็น "ระบบ Booking" ไม่รู้ว่าตัวเดียวกัน
  2. ราคา booking-system 25,000 -> 9,900 ให้ตรงกับหน้าขายและมติราคา 3 tier
  3. ตัด feature ที่ทำไม่ได้จริงออก 4 บรรทัด (SLA / Onsite ทั่วประเทศ / Deploy 7 วัน / ROI)
     ทั้ง 4 ข้อนี้ถ้าเซ็นสัญญาแล้วทำไม่ได้ = ผิดสัญญาและอาจถูกเรียกเงินคืน
  4. ย้ายป้าย "แนะนำ" จาก 3 ตัวที่ยังไม่มีของ (Chatbot / Lead Gen / Custom Agent)
     ไปที่ QueueFlow ซึ่งเป็นตัวเดียวที่ส่งมอบได้จริงพรุ่งนี้
  5. ซ่อน LMS 45,000 เพราะยังไม่มีของเลยแม้แต่ชิ้นเดียว

ไม่ซ่อน POS แล้ว — เจ้าของแจ้ง 27 ส.ค. 69 ว่า pos.noodee-bootbiz.com เสร็จและ live
แต่ยังไม่ติดป้ายแนะนำเพราะยังไม่มีหน้าขายและยังไม่มีรูปปก

DB ตัวนี้คือ production (peyo_agent @192.168.1.2) แก้แล้วเห็นบนเว็บทันที
สคริปต์จึงสำรองของเดิมลงไฟล์ก่อนเสมอ และไม่ลงมือจนกว่าจะใส่ --apply

ใช้:  venv\Scripts\python.exe scripts/fix_service_content.py            (ดูว่าจะแก้อะไร)
      venv\Scripts\python.exe scripts/fix_service_content.py --apply    (ลงมือจริง)
"""

import argparse
import io
import json
import os
import sys
from datetime import date

import django

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_automate.settings")
django.setup()

from pages.models import Service  # noqa: E402

BACKUP = os.path.join(ROOT, "scripts", "article_assets",
                      "backup_services_%s.json" % date.today().isoformat())

# feature ที่ต้องตัดออก — คีย์คือ slug ค่าคือข้อความที่ต้องไม่มีอีก
DROP_FEATURES = {
    "ai-chatbot": ["ทดสอบและ Deploy ภายใน 7 วัน"],
    "ai-workflow-automation": ["ROI เฉลี่ย 3-6 เดือน"],
    "custom-ai-agent": ["SLA รับประกัน Uptime 99.5%"],
    "ai-hardware-integration": ["ดูแลระบบ Onsite ทั่วประเทศ"],
}

# ฟิลด์ที่ตั้งค่าใหม่ตรง ๆ
FIELD_UPDATES = {
    "booking-system": {
        "name": "QueueFlow — ระบบจองคิวออนไลน์",
        "price_start": 9900,
        "is_featured": True,
    },
    "ai-chatbot": {"is_featured": False},
    "ai-lead-generation": {"is_featured": False},
    "custom-ai-agent": {"is_featured": False},
    "online-course-lms": {"status": "draft"},
}


def backup():
    rows = []
    for s in Service.objects.all().order_by("id"):
        rows.append({
            "id": s.pk, "slug": s.slug, "name": s.name, "tagline": s.tagline,
            "price_start": s.price_start, "price_label": s.price_label,
            "features": s.features, "status": s.status,
            "is_featured": s.is_featured, "display_order": s.display_order,
        })
    io.open(BACKUP, "w", encoding="utf-8").write(
        json.dumps(rows, ensure_ascii=False, indent=2))
    print("สำรองบริการ %s รายการไว้ที่ %s\n" % (len(rows), BACKUP))


def plan_changes():
    """คืนรายการสิ่งที่จะเปลี่ยน โดยยังไม่เขียนอะไรลง DB"""
    changes = []
    for slug, lines in DROP_FEATURES.items():
        s = Service.objects.filter(slug=slug).first()
        if s is None:
            print("!! ไม่พบบริการ slug=%s — ข้าม" % slug)
            continue
        keep = [ln for ln in s.features.splitlines()
                if ln.strip() not in [x.strip() for x in lines]]
        if len(keep) != len(s.features.splitlines()):
            changes.append((s, "features", "\n".join(keep)))

    for slug, fields in FIELD_UPDATES.items():
        s = Service.objects.filter(slug=slug).first()
        if s is None:
            print("!! ไม่พบบริการ slug=%s — ข้าม" % slug)
            continue
        for field, value in fields.items():
            if getattr(s, field) != value:
                changes.append((s, field, value))
    return changes


def show(changes):
    for s, field, value in changes:
        if field == "features":
            dropped = set(s.features.splitlines()) - set(value.splitlines())
            for line in dropped:
                print("  #%s %-28s ตัด feature: %s" % (s.pk, s.slug, line))
        else:
            print("  #%s %-28s %s: %r -> %r"
                  % (s.pk, s.slug, field, getattr(s, field), value))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true", help="ลงมือจริง")
    args = p.parse_args()

    backup()
    changes = plan_changes()
    if not changes:
        print("ไม่มีอะไรต้องแก้ — ข้อมูลตรงกับของจริงอยู่แล้ว")
        return

    print("สิ่งที่จะเปลี่ยน %s จุด:" % len(changes))
    show(changes)

    if not args.apply:
        print("\nยังไม่ได้ลงมือ — ใส่ --apply เมื่อพร้อม")
        return

    # รวมการเปลี่ยนของ service เดียวกันไว้ save ครั้งเดียว
    touched = {}
    for s, field, value in changes:
        setattr(s, field, value)
        touched[s.pk] = s
    for s in touched.values():
        s.save()
    print("\nบันทึกแล้ว %s บริการ" % len(touched))


if __name__ == "__main__":
    main()
