import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_automate.settings")
django.setup()

from pages.models import Service

extra = {
    "ai-chatbot": [
        "จำบทสนทนาและ Context ลูกค้าแต่ละราย",
        "ตอบหลายภาษา ไทย/อังกฤษ/จีน",
        "ส่งแคตตาล็อก/โปรโมชันอัตโนมัติ",
        "Handoff ให้ Staff เมื่อต้องการ",
        "ตั้ง Greeting/เมนูได้เองไม่ต้องโค้ด",
        "ทดสอบและ Deploy ภายใน 7 วัน",
    ],
    "ai-lead-generation": [
        "คัดกรอง Lead ปลอมออกอัตโนมัติ",
        "A/B Test ข้อความ Follow-up",
        "สร้าง Landing Page ดักจับ Lead",
        "แบ่งกลุ่ม Lead ตาม Product สนใจ",
        "ติดตาม Lead ข้ามช่องทางได้",
        "Dashboard Conversion Rate รายวัน",
    ],
    "ai-workflow-automation": [
        "ดึงข้อมูลข้ามระบบโดยไม่ต้องพิมพ์ซ้ำ",
        "Approve งานผ่าน LINE ได้เลย",
        "จัดลำดับงานอัตโนมัติตาม Priority",
        "Backup ข้อมูลและ Log ทุก Action",
        "ปรับ Workflow ได้เองไม่ต้องรอ IT",
        "รองรับทีมหลายสาขาพร้อมกัน",
    ],
    "custom-ai-agent": [
        "วิเคราะห์เอกสาร/ใบเสนอราคาอัตโนมัติ",
        "เรียนรู้และปรับปรุงจากการใช้งานจริง",
        "ตั้ง Permission แยกตาม Role ทีม",
        "ทดสอบใน Sandbox ก่อน Deploy จริง",
        "อัปเดต Logic ได้โดยไม่หยุดระบบ",
        "SLA รับประกัน Uptime 99.5%",
    ],
    "ai-hardware-integration": [
        "นับคน/รถ/สินค้าจากกล้องอัตโนมัติ",
        "แจ้งเตือนทันทีเมื่อเกิดเหตุผิดปกติ",
        "ควบคุมอุปกรณ์ระยะไกลผ่านแอป",
        "เก็บ Log ภาพ/เซ็นเซอร์ย้อนหลัง 90 วัน",
        "ขยายจุดติดตั้งได้โดยไม่เปลี่ยนระบบ",
        "ติดตั้งและอบรมทีมงาน Onsite",
    ],
    "booking-massage": [
        "ลูกค้าเลือก Therapist ที่ชอบได้เอง",
        "ยืนยันนัดและ Remind อัตโนมัติ",
        "จัดการ Walk-in + Online พร้อมกัน",
        "สะสมแต้มและแลกรางวัลในระบบ",
        "รายงานบริการยอดนิยมรายเดือน",
        "รองรับหลายสาขาจากระบบเดียว",
    ],
    "online-exam-system": [
        "กำหนดเวลาและตัดสิทธิ์อัตโนมัติ",
        "แสดงผลคะแนนทันทีหลังส่งข้อสอบ",
        "เปรียบเทียบผลกับค่าเฉลี่ยกลุ่ม",
        "ออกใบรับรองผลสอบอัตโนมัติ",
        "จัดการหลายห้องสอบพร้อมกัน",
        "เข้าสอบได้ทุก Device ไม่ต้องติดตั้ง",
    ],
    "online-course-lms": [
        "ล็อคบทเรียนตามลำดับ ข้ามไม่ได้",
        "Live สดและบันทึกในระบบเดียว",
        "ส่ง Assignment และตรวจงานออนไลน์",
        "แจ้งเตือนผู้เรียนที่หายหน้าไป",
        "ขายคอร์สผ่านระบบ Affiliate ได้",
        "Analytics ผู้เรียนรายคนรายบท",
    ],
}

for slug, new_features in extra.items():
    svc = Service.objects.filter(slug=slug).first()
    if not svc:
        print(f"  NOT FOUND: {slug}")
        continue
    existing = [f.strip() for f in svc.features.splitlines() if f.strip()]
    combined = existing + new_features
    svc.features = "\n".join(combined)
    svc.save(update_fields=["features"])
    print(f"  OK {slug}: {len(existing)} + {len(new_features)} = {len(combined)} features")

print("\nDone")
