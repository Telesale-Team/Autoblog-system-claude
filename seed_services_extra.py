import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_automate.settings")
django.setup()

from pages.models import Service

services = [
    dict(
        name="เว็บไซต์ Booking ร้านนวด",
        slug="booking-massage",
        tagline="ลูกค้าจองได้ตลอด 24 ชม. โดยไม่ต้องรับโทรศัพท์",
        description="ระบบจองนัดออนไลน์สำหรับร้านนวด สปา และคลินิกความงาม ช่วยให้ลูกค้าเลือกวัน เวลา และ therapist ได้เองผ่านมือถือ เจ้าของร้านจัดการตารางงานและรายได้ได้จากหน้าจอเดียว เหมาะสำหรับร้านที่อยากลดงาน admin และรับลูกค้าได้มากขึ้นโดยไม่ต้องเพิ่มพนักงาน",
        icon="bi-calendar-check",
        price_start=25000,
        price_label="เริ่มต้น",
        features="""จองออนไลน์ 24 ชม. ผ่านมือถือ
จัดตาราง therapist ไม่ชนกัน
แจ้งเตือน LINE อัตโนมัติ
รับชำระเงินออนไลน์ได้ทันที
แดชบอร์ดรายได้และสถิติร้าน
ระบบสมาชิกและโปรโมชั่นลูกค้าประจำ""",
        is_featured=False,
        display_order=6,
    ),
    dict(
        name="ระบบข้อสอบออนไลน์",
        slug="online-exam-system",
        tagline="สร้างข้อสอบใน 10 นาที ตรวจอัตโนมัติ รู้ผลทันที",
        description="แพลตฟอร์มสร้างและจัดการข้อสอบออนไลน์สำหรับโรงเรียน สถาบันกวดวิชา และองค์กรที่ต้องทดสอบพนักงาน รองรับข้อสอบหลายประเภท ตรวจและประมวลผลอัตโนมัติพร้อมรายงานรายบุคคล เหมาะสำหรับทีมที่ต้องการลดภาระการตรวจกระดาษและเห็นผลการเรียนรู้ของผู้สอบได้ชัดเจน",
        icon="bi-pencil-square",
        price_start=35000,
        price_label="เริ่มต้น",
        features="""สร้างข้อสอบได้หลายประเภทคำถาม
ตรวจและให้คะแนนอัตโนมัติ
วิเคราะห์ผลรายบุคคลและรายกลุ่ม
ระบบสุ่มข้อและสลับตัวเลือก
ป้องกันทุจริตด้วย proctoring เบื้องต้น
ส่งออกรายงานผล PDF และ Excel""",
        is_featured=False,
        display_order=7,
    ),
    dict(
        name="ระบบคอร์สเรียนออนไลน์",
        slug="online-course-lms",
        tagline="เปิดคอร์สออนไลน์ได้เอง ขายได้ทันที ไม่ต้องง้อแพลตฟอร์มใหญ่",
        description="ระบบ LMS ส่วนตัวสำหรับอาจารย์ โค้ช และสถาบันที่ต้องการขาย online course บนแบรนด์ของตัวเอง อัปโหลดวิดีโอและเอกสาร เชื่อมระบบชำระเงิน ติดตามความก้าวหน้าผู้เรียน และออกใบเซอร์ติฟิเคตได้ในที่เดียว เหมาะสำหรับผู้สอนที่อยากมีรายได้ online โดยไม่เสียค่า commission ให้แพลตฟอร์มอื่น",
        icon="bi-play-circle",
        price_start=45000,
        price_label="เริ่มต้น",
        features="""อัปโหลดวิดีโอและเอกสารไม่จำกัด
รับชำระเงินผ่าน QR และบัตรเครดิต
ติดตามความก้าวหน้าผู้เรียนรายคน
ออกใบเซอร์ติฟิเคตอัตโนมัติ
ระบบ quiz และแบบทดสอบท้ายบท
แบรนด์เป็นของคุณ 100% ไม่มีโลโก้เรา""",
        is_featured=False,
        display_order=8,
    ),
]

for s in services:
    obj, new = Service.objects.update_or_create(slug=s["slug"], defaults=s)
    status = "Created" if new else "Updated"
    print(f"  {status}: {obj.name}")

print(f"\nDone — {len(services)} services processed")
