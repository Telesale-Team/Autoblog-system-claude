import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_automate.settings")
django.setup()

from pages.models import Service

services = [
    dict(
        name="AI Chatbot สำหรับธุรกิจ",
        slug="ai-chatbot",
        tagline="บอทสนทนาอัจฉริยะที่ตอบแทนทีมได้ตลอด 24 ชั่วโมง",
        description="สร้าง AI Chatbot บน LINE / Facebook / เว็บไซต์ ที่เข้าใจภาษาไทยได้อย่างเป็นธรรมชาติ ตอบคำถาม รับออเดอร์ และส่ง Leads เข้า CRM โดยอัตโนมัติ ไม่ต้องจ้างพนักงานเพิ่ม",
        icon="bi-robot",
        price_start=15000,
        price_label="เริ่มต้น",
        features="""ตอบคำถามอัตโนมัติ 24/7
เชื่อมต่อ LINE OA / Facebook Page / เว็บไซต์
เข้าใจภาษาไทยตามบริบทธุรกิจคุณ
ส่ง Lead เข้า CRM อัตโนมัติ
Dashboard ดูสถิติการสนทนา
รองรับลูกค้าพร้อมกันไม่จำกัด""",
        is_featured=True,
        display_order=1,
    ),
    dict(
        name="AI Lead Generation",
        slug="ai-lead-generation",
        tagline="ดึง Lead คุณภาพสูงเข้าธุรกิจโดยอัตโนมัติด้วย AI",
        description="ระบบ AI ที่วิเคราะห์พฤติกรรมผู้เยี่ยมชมเว็บ คัดกรอง Lead อัตโนมัติ ส่ง Follow-up Email/LINE และแจ้งเตือนทีมขายเมื่อ Lead พร้อม Close",
        icon="bi-graph-up-arrow",
        price_start=20000,
        price_label="ต่อเดือน",
        features="""วิเคราะห์ Lead Score อัตโนมัติ
ส่ง Follow-up อัตโนมัติทาง LINE / Email
แจ้งเตือนทีมขายแบบ Real-time
ทำนายโอกาสปิดดีล
Integrate กับ CRM ที่มีอยู่
Report ประสิทธิภาพ Lead รายสัปดาห์""",
        is_featured=True,
        display_order=2,
    ),
    dict(
        name="AI Workflow Automation",
        slug="ai-workflow-automation",
        tagline="ลด Manual Work ซ้ำซากด้วย AI Workflow อัตโนมัติ",
        description="วิเคราะห์ขั้นตอนงานภายใน แล้วออกแบบ Workflow อัตโนมัติด้วย AI เชื่อมต่อทุก Tool ที่ธุรกิจคุณใช้อยู่ ไม่ว่าจะเป็น Excel, Google Sheets, LINE, Email หรือระบบ ERP",
        icon="bi-diagram-3",
        price_start=25000,
        price_label="ต่อโปรเจกต์",
        features="""วิเคราะห์ Process ที่ซ้ำซากในองค์กร
เชื่อมต่อ Google Workspace / Microsoft 365
Auto-generate รายงานรายวัน / รายสัปดาห์
แจ้งเตือนและ Escalation อัตโนมัติ
ลด Human Error ในงานข้อมูล
ROI เฉลี่ย 3-6 เดือน""",
        is_featured=False,
        display_order=3,
    ),
    dict(
        name="Custom AI Agent",
        slug="custom-ai-agent",
        tagline="AI Agent เฉพาะองค์กร ทำงานได้ทุกอย่างที่คุณต้องการ",
        description="พัฒนา AI Agent แบบ Custom ที่ทำงานได้ตาม Process เฉพาะของธุรกิจคุณ ตั้งแต่ Agent วิเคราะห์ข้อมูล, ตรวจเอกสาร, ออกใบเสนอราคา ไปจนถึง Agent ที่สั่งงานระบบอื่นได้เอง",
        icon="bi-cpu",
        price_start=50000,
        price_label="ต่อโปรเจกต์",
        features="""ออกแบบตาม Business Logic ของคุณ
เชื่อมต่อ Database และ API ภายใน
ทำงานได้หลาย Step โดยอัตโนมัติ
รองรับ Multi-agent Collaboration
มี Logging และ Audit Trail
พร้อม Support และ Maintenance""",
        is_featured=True,
        display_order=4,
    ),
    dict(
        name="AI + Hardware Integration",
        slug="ai-hardware-integration",
        tagline="เชื่อม AI เข้ากับอุปกรณ์จริงในสถานประกอบการ",
        description="นำ AI ไปใช้กับ Hardware จริง ไม่ว่าจะเป็น กล้อง CCTV วิเคราะห์พฤติกรรม, Sensor IoT แจ้งเตือนอัตโนมัติ, หรือระบบ Kiosk รับออเดอร์ด้วย AI สำหรับร้านค้าและโรงงาน",
        icon="bi-hdd-network",
        price_start=80000,
        price_label="ต่อโปรเจกต์",
        features="""Camera AI วิเคราะห์ภาพ Real-time
IoT Sensor + AI Alert System
Kiosk / Self-service ด้วย AI
เชื่อมต่อ POS / ERP / MES
ติดตั้ง On-premise หรือ Cloud
ดูแลระบบ Onsite ทั่วประเทศ""",
        is_featured=False,
        display_order=5,
    ),
]

created = 0
for s in services:
    obj, new = Service.objects.update_or_create(slug=s["slug"], defaults=s)
    if new:
        created += 1
        print(f"  Created: {obj.name}")
    else:
        print(f"  Updated: {obj.name}")

print(f"\nDone — {created} created, {len(services)-created} updated")
