"""แผนพัฒนาระบบ (Roadmap) — แหล่งความจริงเดียวของสถานะงานทั้งโปรเจกต์

ไฟล์นี้คือ "แผน" ที่คนเป็นคนคุม ไม่ใช่สิ่งที่ระบบเดาเอง
หน้า /owner/roadmap/ อ่านจากไฟล์นี้ที่เดียว (เห็นได้เฉพาะ superuser)

กติกาการใช้งาน — สำคัญ อ่านก่อนแก้:
  1. ปิดงานเรื่องไหนเสร็จ ให้เปลี่ยน status ของเรื่องนั้นเป็น DONE ทันทีในคอมมิตเดียวกับโค้ด
  2. ขึ้นเฟสใหม่ ให้แก้ CURRENT และย้าย IN_PROGRESS ให้มีเฟสเดียวเสมอ (มีเทสคุมอยู่)
  3. งานที่ไม่มีอยู่ในไฟล์นี้ = งานนอกแผน ต้องถามเจ้าของก่อนลงมือ
  4. ห้ามลบเรื่องที่ทำเสร็จแล้วออก — ประวัติอยู่ใน git แล้ว แต่หน้าจอต้องเห็นภาพรวมครบ

ทำไมไม่ให้ระบบตรวจสถานะเอง: "มีโค้ดแล้ว" ไม่เท่ากับ "ใช้งานได้จริงและทดสอบแล้ว"
ตัวเลขจริงจากฐานข้อมูล (metrics) จึงแสดง "ควบคู่" กับสถานะที่คนกำหนด ไม่ใช่แทนที่

ทำไมเป็นไฟล์ Python ไม่ใช่ตารางใน DB: git hook ตรวจได้ว่าแผนถูกแก้พร้อมโค้ดหรือเปล่า
ประวัติการเปลี่ยนแผนอยู่ใน git log และ deploy แล้วแผนไปพร้อมโค้ดเสมอ ไม่หลุดคนละชุด

ที่มา: ยกระบบมาจากโปรเจกต์ StockProject (MainProject/core/roadmap.py) ตามที่เจ้าของสั่ง 26 ส.ค. 2569
"""

from datetime import date

# ---------------------------------------------------------------------------
# สถานะของแต่ละเรื่อง
# ---------------------------------------------------------------------------
DONE = 'done'                # ทำเสร็จและใช้งานได้จริงแล้ว
EARLY = 'early'              # เสร็จแล้ว แต่ทำล่วงหน้าข้ามคิวมาจากเฟสอื่น
IN_PROGRESS = 'in_progress'  # กำลังลงมืออยู่ตอนนี้
TODO = 'todo'                # ยังไม่เริ่ม
BLOCKED = 'blocked'          # ลงมือไม่ได้ ติดรอการตัดสินใจ

STATUS_META = {
    DONE:        {'label': 'เสร็จแล้ว',       'badge': 'success',   'icon': 'bi bi-check-lg'},
    EARLY:       {'label': 'เสร็จ (ข้ามคิว)',  'badge': 'info',      'icon': 'bi bi-fast-forward-fill'},
    IN_PROGRESS: {'label': 'กำลังทำ',         'badge': 'warning',   'icon': 'bi bi-hammer'},
    TODO:        {'label': 'ยังไม่เริ่ม',      'badge': 'secondary', 'icon': 'bi bi-circle'},
    BLOCKED:     {'label': 'ติดรอตัดสินใจ',   'badge': 'danger',    'icon': 'bi bi-hand-index'},
}

# นับเป็น "ทำแล้ว" ตอนคำนวณเปอร์เซ็นต์
COMPLETED_STATUSES = (DONE, EARLY)


# ---------------------------------------------------------------------------
# กำลังทำอะไรอยู่ตอนนี้ — แถบบนสุดของหน้า
# ---------------------------------------------------------------------------
CURRENT = {
    'phase': 8,
    'task': 'เริ่มที่ SegmentProfile — โปรไฟล์ 5 มิติต่อ segment เป็นแหล่งความจริงเดียว',
    'owner': 'ai-orchestrator',
    'started': date(2026, 8, 26),
    'note': '**26 ส.ค. 2569 เจ้าของยืนยันสถานะเฟส 1-6 ว่าตรง (มติ RM-1) และสั่งเดินงานต่อ** '
            '· เฟส 7 ปิดครบในวันเดียวกัน — ระบบแผนพัฒนายกมาจาก StockProject '
            'และสะสางปฏิทินไป 88 รายการตามมติ RM-2 (งานค้าง 162 -> 74) '
            '· เฟส 8 เริ่มที่ SegmentProfile ก่อน เพราะเป็นเรื่องที่ผลกระทบสูงสุดและเสี่ยงต่ำสุด '
            'ไม่พังของเดิม และเป็นฐานให้เรื่องอื่นในเฟสนี้ต่อยอด '
            '· ลำดับที่ตั้งใจ: SegmentProfile -> ต่อเข้า skill diagram/cover -> '
            'รายการ AI-slop ไทย -> skill expert-panel-th -> เก็บคะแนนลง DB -> ประตูอนุมัติ '
            '· **หน้าจอในเฟสนี้ต้องผ่าน Frontend Designer ก่อนเสมอ** '
            '· ยังค้าง: มติ RM-3 ว่างานจริง 29 รายการที่เลยกำหนดแต่ไม่มีในแผนจะเอาไปไว้ไหน',
}


# ---------------------------------------------------------------------------
# แผน 8 เฟส — เฟสใหม่ให้ต่อท้ายเสมอ ห้ามแทรกกลางแล้วดันเลขเดิม
#
# metrics: key ที่ต้องมีใน dict ที่ view ส่งเข้ามา (ดู dashboard.views.roadmap_view)
# calendar: คำค้นในหัวข้อ CalendarEvent — ใช้เทียบว่าแผนกับปฏิทินตรงกันไหม
# ---------------------------------------------------------------------------
PHASES = [
    {
        'no': 1,
        'name': 'เว็บไซต์สาธารณะ และบล็อก',
        'goal': 'มีเว็บของตัวเองที่เผยแพร่บทความได้ และหน้าตาเป็นแบรนด์เดียวกันทั้งเว็บ',
        'status': DONE,
        'note': 'ฐานรากของทุกอย่าง เสร็จตั้งแต่ช่วงแรกของโปรเจกต์ (พ.ค. 2569)',
        'metrics': [
            {'key': 'articles', 'label': 'บทความทั้งหมด'},
            {'key': 'articles_published', 'label': 'เผยแพร่แล้ว'},
            {'key': 'services', 'label': 'บริการบนเว็บ'},
        ],
        'items': [
            {'name': 'หน้าเว็บสาธารณะ — หน้าแรก บริการ เกี่ยวกับเรา ติดต่อ', 'status': DONE},
            {'name': 'ระบบบล็อก — บทความ หมวดหมู่ แท็ก', 'status': DONE},
            {'name': 'ตัวแก้บทความ CKEditor + รูปปก + ปุ่มแชร์ 3 ช่องทาง', 'status': DONE},
            {'name': 'Design System สีกรม+ทอง เก็บ token ที่ main.css ที่เดียว', 'status': DONE,
             'note': 'Option A Navy+Gold · ฟอนต์ Sarabun ห้าม italic · hover เป็นสีทองทุกที่'},
            {'name': 'ไฟล์ static และ media — WhiteNoise เสิร์ฟ static, re_path เสิร์ฟ media', 'status': DONE},
            {'name': 'Portfolio และ Case Studies', 'status': DONE},
            {'name': 'SEO meta และ sitemap', 'status': DONE},
        ],
    },
    {
        'no': 2,
        'name': 'หลังบ้านเจ้าของกิจการ (Owner Dashboard)',
        'goal': 'บริหารธุรกิจทุกด้านจากหน้าเดียว ไม่ต้องเข้า Django admin',
        'status': DONE,
        'note': 'แผนเดิมวางไว้ 29 เมนู (docs/feature_roadmap.html 16 พ.ค. 69) '
                'ตอนนั้นมี 14 เมนู เหลือทำ 15 เมนู — ตอนนี้ทำครบเกือบหมดแล้ว '
                'เหลือกลุ่มที่ยังเป็นหน้า "เร็วๆ นี้" อยู่ 4 เมนู',
        'menu': {'label': 'หลังบ้าน', 'icon': 'bi bi-speedometer2'},
        'metrics': [
            {'key': 'leads', 'label': 'Leads'},
            {'key': 'customers', 'label': 'ลูกค้า'},
        ],
        'items': [
            {'name': 'หน้าหลัก Dashboard และ Analytics', 'status': DONE},
            {'name': 'ปฏิทินงาน (FullCalendar + DB)', 'status': DONE,
             'note': 'ดูเฟส 7 ด้วย — ปฏิทินกลายเป็นกองงานค้าง ต้องสะสางให้ตรงกับแผน'},
            {'name': 'Leads และ Pipeline', 'status': DONE},
            {'name': 'Revenue และ KPI Dashboard', 'status': DONE},
            {'name': 'จัดการบทความ และ Content Backlog', 'status': DONE},
            {'name': 'ลูกค้า / ต่อสัญญา / ใบเสนอราคา (crm)', 'status': DONE},
            {'name': 'แคมเปญ / Keywords (marketing)', 'status': DONE},
            {'name': 'ใบแจ้งหนี้ / ค่าใช้จ่าย (finance)', 'status': DONE},
            {'name': 'สัญญา (legal)', 'status': DONE},
            {'name': 'AI Projects / Prompt Library / QA Log (operations)', 'status': DONE},
            {'name': 'หน้า Design System', 'status': DONE},
            {'name': 'คู่มือทีม / ทีม AI Agents / จัดการเนื้อหาเว็บ / ตั้งค่าระบบ', 'status': DONE},
            {'name': 'มาตรฐานหน้าจอเดียวกันทุกหน้า (settings-hero + scard)', 'status': DONE},
            {'name': 'Team Standup — สรุปรายวันของแต่ละ agent', 'status': TODO,
             'note': 'เมนู #03 ในแผนเดิม ยังไม่ได้ทำ · ตอนนี้หน้า /owner/team/ '
                     'เป็นหน้ารายชื่อ agent ไม่ใช่ standup'},
            {'name': 'LOI / Retail / Gap / Savings — 4 เมนูที่ยังเป็นหน้า "เร็วๆ นี้"', 'status': TODO,
             'note': 'อยู่ใน dashboard/urls.py ชี้ไป views.coming_soon '
                     'ต้องถามเจ้าของก่อนว่ายังต้องการอยู่ไหม หรือถอดออกจากเมนู'},
        ],
    },
    {
        'no': 3,
        'name': 'ทีม AI Agent และ Skills',
        'goal': 'มีทีมงานที่เรียกใช้ได้จริง แต่ละตัวมีขอบเขตชัด ไม่ทับกัน',
        'status': DONE,
        'note': 'ครบตามที่วางไว้ · เพิ่ม agent ใหม่ให้ใช้ skill agent-creator เพื่อคุมคุณภาพ',
        'items': [
            {'name': 'Agent 26 ตัว พร้อม system prompt และ frontmatter', 'status': DONE},
            {'name': 'Skills 12 ตัวใน .claude/skills/', 'status': DONE},
            {'name': 'Workflow A-F และ Routing Logic', 'status': DONE},
            {'name': 'Alias สั้น — หนูดี / ลอย / ยูโร', 'status': DONE},
            {'name': 'นักเขียนแยก segment 6 ตัว + Django user accounts', 'status': DONE},
            {'name': 'Graphic Designer (#25) และ Market Research Analyst (#26)', 'status': DONE},
            {'name': 'Meta-skill สร้าง agent และ skill ใหม่ตาม rubric', 'status': DONE},
        ],
    },
    {
        'no': 4,
        'name': 'เครื่องมือผลิตคอนเทนต์',
        'goal': 'ผลิตบทความพร้อมภาพปกและ diagram ครบชุดโดยไม่ต้องทำมือทีละชิ้น',
        'status': DONE,
        'note': 'เครื่องมือครบแล้ว แต่คอร์ส Python 101 ยังเขียนไม่จบ และยังไม่มีระบบ Series บนเว็บ',
        'metrics': [
            {'key': 'python101', 'label': 'บทเรียน Python 101'},
            {'key': 'backlog', 'label': 'Content Backlog'},
        ],
        'items': [
            {'name': 'Article Workflow 4 ขั้น — เขียน / ภาพปก / diagram / ประกอบร่าง', 'status': DONE},
            {'name': 'สร้างภาพปกด้วย FLUX + น้องหนูดี + Pillow', 'status': DONE},
            {'name': 'สร้าง diagram อัตโนมัติทุกหัวข้อ H2', 'status': DONE},
            {'name': 'บทความแบบเอกสาร (layout=docs) พร้อมสารบัญอัตโนมัติ', 'status': DONE},
            {'name': 'เขียนบทความด้วย Markdown ได้ (แก้ปัญหา CKEditor กิน callout/SVG)', 'status': DONE},
            {'name': 'สายข่าว AI (Workflow F) — ยูโรล่าข่าว ส่งต่อให้นักเขียน', 'status': DONE},
            {'name': 'คอร์ส Python 101 — EP0 ถึง EP4', 'status': DONE,
             'calendar': 'Python 101'},
            {'name': 'คอร์ส Python 101 — EP5 ถึง EP12', 'status': TODO,
             'note': 'เหลืออีก 8 ตอน: ลิสต์+ลูป, dict, ฟังก์ชัน, ไฟล์ CSV, อ่าน error, '
                     'pip, API, Capstone LINE · ปล่อยสัปดาห์ละตอนตามที่ตกลงไว้'},
            {'name': 'ภาพปกของคอร์ส Python 101', 'status': TODO,
             'note': 'ยังไม่มีสักตอน ทั้งที่ทุกบทความอื่นมีปก'},
            {'name': 'ระบบ Series/EP บนเว็บ — ปุ่มก่อนหน้า/ถัดไป และหน้าสารบัญคอร์ส', 'status': BLOCKED,
             'note': 'ติดรอเจ้าของเคาะว่าจะสร้าง Series model หรือใช้ tag '
                     '· ตอนนี้คนเรียนต้องหาตอนถัดไปเอง'},
        ],
    },
    {
        'no': 5,
        'name': 'QueueFlow — ระบบจองคิว (สินค้าตัวที่ 6)',
        'goal': 'มีหน้าขายและเว็บทดลองที่พา prospect ไปถึงการปิดดีลแรกได้',
        'status': DONE,
        'note': 'หน้าขายขึ้นจริงแล้วทั้ง 4 เวอร์ชัน แต่ยังไม่มีมติว่าใช้ตัวไหนเป็นตัวจริง '
                'และราคายังไม่ผ่าน Money Manager — ยังปิดดีลไม่ได้จนกว่าจะเคาะ 3 เรื่องนี้',
        'metrics': [
            {'key': 'queueflow_pages', 'label': 'หน้าขายที่ทำแล้ว'},
        ],
        'items': [
            {'name': 'หน้าขาย V1 ขึ้นจริงที่ /services/booking-system/', 'status': DONE},
            {'name': 'หน้าขาย V2 / V3 / V4 สำหรับทดสอบ A/B', 'status': DONE},
            {'name': 'วิจัยตลาดและคู่แข่งโดย Agent #26', 'status': DONE,
             'note': 'ได้ข้อมูลจริงมีแหล่งอ้างอิง — Fresha ฿350-525/ด. ถูกกว่าที่เคยเข้าใจ '
                     'ห้ามเคลมว่าคู่แข่งแพงเชิง subscription'},
            {'name': 'เว็บทดลอง booking.noodee-bootbiz.com + ข้อมูลตัวอย่าง 84 คิว', 'status': DONE},
            {'name': 'ภาพบริการ 15 รูปด้วย FLUX อัปขึ้นเว็บทดลองแล้ว', 'status': DONE},
            {'name': 'สร้างบัญชี demo_owner ให้ prospect ลองเล่น', 'status': TODO,
             'note': 'สคริปต์พร้อมที่ scripts/noodee_demo_account.py ยังรอเจ้าของยืนยัน',
             'calendar': 'demo'},
            {'name': 'ราคา 3 tiers ผ่าน Money Manager', 'status': BLOCKED,
             'note': 'Starter ฿9,900+฿990/ด. | Pro ฿19,900+฿1,990/ด. | Multi ฿39,900+฿3,990/ด. '
                     'ยังเป็นตัวเลขข้อเสนอ ยังไม่ final'},
            {'name': 'ตัดสินใจเรื่องค่าติดตั้ง (setup fee)', 'status': BLOCKED,
             'note': 'Agent #26 escalate ไว้ — คู่แข่งแทบไม่มี setup fee ของเราเก็บ '
                     '฿9,900-39,900 เป็น friction ที่ทำให้ปิดดีลยากขึ้น'},
            {'name': 'เลือกว่า V1-V4 ตัวไหนเป็นหน้าขายตัวจริง', 'status': BLOCKED,
             'note': 'ทำไว้ 4 เวอร์ชันแต่ยังไม่มีมติ ปล่อยไว้แบบนี้ทำให้ดูแลซ้ำซ้อน 4 ไฟล์'},
        ],
    },
    {
        'no': 6,
        'name': 'ระบบเฝ้าดูโปรเจกต์ลูกค้า (Project Monitor)',
        'goal': 'รู้ได้จากหน้าเดียวว่าระบบที่ส่งมอบลูกค้าไปแล้วยังทำงานอยู่ไหม',
        'status': DONE,
        'note': 'โค้ดเขียนเสร็จแล้วแต่ยังไม่ commit และยังไม่มีข้อมูลจริงสักแถว '
                'ถือว่ายังใช้งานจริงไม่ได้จนกว่าจะ backfill',
        'metrics': [
            {'key': 'ai_projects', 'label': 'โปรเจกต์ในระบบ'},
            {'key': 'deployments', 'label': 'Deployment'},
        ],
        'items': [
            {'name': 'สายโซ่ข้อมูล Service → AIProject → Deployment → HealthCheck', 'status': DONE,
             'note': 'migration 0002_aiproject_service_deployment_healthcheck.py'},
            {'name': 'หน้า /owner/projects/ และหน้ารายละเอียด', 'status': DONE},
            {'name': 'แบ่งกลุ่ม 2 ชั้น + dropdown สลับมุมมอง', 'status': DONE},
            {'name': 'ใส่ข้อมูลระบบที่รันจริงบนเซิร์ฟเวอร์เข้า DB', 'status': TODO,
             'note': 'AIProject ยังมี 0 แถว — ระบบที่รันจริง 5 instance บน 192.168.1.2 '
                     'ยังไม่มีตัวตนในระบบเลย · ห้ามเอา portfolio.CaseStudy 9 ชิ้นมาปน '
                     'เพราะเป็นเคสตัวอย่างการตลาด ไม่ใช่ลูกค้าจริง'},
            {'name': 'ทำ endpoint /api/monitor/ ในระบบฝั่งลูกค้า', 'status': TODO,
             'note': 'สัญญามาตรฐาน Bearer token อ่านอย่างเดียว คืน version, deployed_at, '
                     'db, migrations_pending, metrics[] · ระบบใหม่เสียบแล้วโผล่เองโดยไม่ต้องแก้โค้ดฝั่งเรา'},
        ],
    },
    {
        'no': 7,
        'name': 'ระบบแผนพัฒนา และสะสางปฏิทิน',
        'goal': 'ตอบได้ทุกเมื่อว่าทำถึงไหน เหลือกี่งาน กี่เฟส และแผนต้องโกหกไม่ได้',
        'status': DONE,
        'note': 'ยกระบบมาจากโปรเจกต์ StockProject ตามที่เจ้าของสั่ง 26 ส.ค. 2569 '
                'ปิดครบทั้งเฟสในวันเดียวกัน',
        'menu': {'label': 'แผนพัฒนาระบบ', 'icon': 'bi bi-diagram-3'},
        'metrics': [
            {'key': 'cal_total', 'label': 'งานในปฏิทิน'},
            {'key': 'cal_pending', 'label': 'ยังไม่ปิด'},
            {'key': 'cal_overdue', 'label': 'เลยกำหนดแล้ว'},
        ],
        'items': [
            {'name': 'ไฟล์แผน dashboard/roadmap.py เป็นแหล่งความจริงเดียว', 'status': DONE,
             'calendar': 'core/roadmap.py'},
            {'name': 'เชื่อมแผนกับปฏิทินงานเดิม ให้เห็นว่าตรงกันหรือไม่', 'status': DONE,
             'note': 'item ที่ประกาศ calendar ไว้จะไปนับ CalendarEvent ที่หัวข้อตรงกัน '
                     'แล้วขึ้นป้ายว่าปิดไปกี่รายการ · แถบขวายังสรุปยอดปฏิทินทั้งหมด '
                     'และไล่งานค้างที่เลยกำหนดให้ดู 15 รายการแรก',
             'calendar': 'เชื่อม roadmap'},
            {'name': 'หน้า /owner/roadmap/ แสดงเฟส ความคืบหน้า และงานที่เหลือ', 'status': DONE,
             'note': 'เห็นเฉพาะ superuser คนอื่นได้ 404 · ใช้ settings-hero + scard '
                     'ตามมาตรฐานเดิม ยังไม่ผ่าน Frontend Designer ตรวจ',
             'calendar': 'หน้า /owner/roadmap/'},
            {'name': 'git hook บล็อก commit ที่เปลี่ยนโครงสร้างแต่ไม่แก้แผน', 'status': DONE,
             'note': 'ทดสอบแล้วบล็อกได้จริง · ครอบคลุม models/urls/migrations '
                     'และ .claude/agents,skills ด้วย เพราะ agent กับ skill ก็คือความสามารถของระบบ '
                     '· clone ใหม่ต้องสั่ง git config core.hooksPath .githooks หนึ่งครั้ง',
             'calendar': 'pre-commit hook'},
            {'name': 'เทสคุมแผน — เฟส in_progress ต้องมีเฟสเดียว และสิทธิ์เข้าหน้า', 'status': DONE,
             'note': 'dashboard/tests_roadmap.py 15 เทส ผ่านหมด · รันด้วย USE_MYSQL=False '
                     'เพราะ user peyo สร้าง test database บน MySQL ไม่ได้',
             'calendar': 'เทสคุมแผน'},
            {'name': 'สะสางปฏิทิน — ปิดงานค้างที่ไม่เป็นความจริงแล้ว', 'status': DONE,
             'note': 'ทำตามมติ RM-2 เมื่อ 26 ส.ค. 2569 — ปิดเป็นกลุ่ม 88 รายการ '
                     '(พิธีกรรมประจำที่เลยกำหนด 29 + แผน 60 วันที่ roadmap มาแทนแล้ว 59) '
                     '· ใช้วิธี is_completed=True **ไม่ลบ** ทุกรายการกดคืนได้ '
                     '· ผลลัพธ์ งานค้าง 162 -> 74 · เลยกำหนด 131 -> 43 '
                     '· เก็บงานอนาคต บทความ 14 รายการ และงานจริงที่เลยกำหนดอีก 29 รายการไว้ '
                     '(29 รายการนั้นยังไม่มีในแผน ดูมติ RM-3)'},
        ],
    },
    {
        'no': 8,
        'name': 'ระบบคุณภาพคอนเทนต์',
        'goal': 'บทความทุกชิ้นมีคะแนนคุณภาพที่ตรวจสอบได้ ก่อนถึงมือคนอ่าน',
        'status': IN_PROGRESS,
        'note': 'ยกไอเดียจาก 2 repo ที่เจ้าของให้ศึกษา 26 ส.ค. 2569 '
                '· AI-Content-Studio (naqashafzal) — ไม่มี license ห้ามใช้โค้ด ยกได้แค่แนวคิด '
                '· ai-marketing-skills (ericosiu) — MIT ใช้โค้ดได้ แต่เป็นภาษาอังกฤษล้วน '
                'ต้องเขียนเวอร์ชันไทยเอง',
        'menu': {'label': 'คุณภาพคอนเทนต์', 'icon': 'bi bi-patch-check'},
        'items': [
            # --- จาก AI-Content-Studio: STYLE_PROFILES 5 มิติ ---
            {'name': 'SegmentProfile — โปรไฟล์ 5 มิติต่อ segment เป็นแหล่งความจริงเดียว',
             'status': DONE,
             'note': '**26 ส.ค. 69 ใช้งานได้จริงแล้ว** — migration 0008 รันบน MySQL peyo_agent '
                     '@192.168.1.2 แล้ว และ seed ครบ 6 กลุ่ม ตรวจแล้วภาษาไทยไม่เพี้ยน '
                     '· ประกอบด้วย model, คำสั่ง seed_segment_profiles (ข้อมูลยกจากไฟล์ agent จริง), '
                     'หน้า Django admin และ API `/owner/api/segment-profiles/[<key>/]` '
                     '· ที่มา: STYLE_PROFILES ใน AI-Content-Studio/api_clients.py '
                     '· แต่ละ segment คุมพร้อมกัน 5 อย่าง: โทนการเขียน / แหล่งค้นข้อมูล / '
                     'สไตล์ diagram / ท่าและอารมณ์ภาพปก / รูปแบบ hook '
                     '· ปัญหาที่แก้: ตอนนี้ agent คุมแค่โทน ส่วน diagram กับปกใครเรียกก็เลือกเอง '
                     'บทความร้านสปาโทนอบอุ่นจึงได้ diagram แข็งๆ กับปกท่า serious ได้ '
                     '· สีกรม+ทองห้ามเปลี่ยน segment ปรับได้แค่สีรอง รูปทรง และอารมณ์'},
            {'name': 'หน้า /owner/segments/ ดูและแก้โปรไฟล์ 5 มิติได้เอง', 'status': DONE,
             'note': 'เจ้าของอนุมัติเพิ่มเข้าแผน 26 ส.ค. 69 · ออกแบบโดย Frontend Designer '
                     '· โครง: การ์ด 6 ใบ + ตารางเทียบ -> คลิกทั้งแถวเข้าไปแก้ทีละกลุ่ม '
                     '· ตัวเลือกสไตล์เป็น radio chip ที่เห็นเป็นภาพจริง (รูปทรง สี ท่าปก) '
                     'ไม่ใช่ dropdown ชื่อค่า '
                     '· สีรองถูกล็อกให้กินพื้นที่ไม่เกิน 5% ของการ์ด และเตือนเมื่อเลือกสีใกล้กรม/ทอง '
                     '· ตรวจค่าซ้ำฝั่งเซิร์ฟเวอร์ทุกช่อง ไม่เชื่อ radio ฝั่งหน้าจออย่างเดียว '
                     '· dashboard/tests_segments.py 12 เทส'},
            {'name': 'ตัวช่วยกลาง scripts/segment_profile.py ให้ script อ่านโปรไฟล์ได้', 'status': DONE,
             'note': 'เจ้าของอนุมัติเพิ่มเข้าแผน 26 ส.ค. 69 — ระหว่างต่อ skill พบว่าถ้าไม่มี '
                     'ตัวกลาง แต่ละ script จะแปลงค่าเองคนละแบบแล้วเพี้ยนกันอีก '
                     '· มี load_segment / diagram_style / cover_prompt / nudee_pose_prompt '
                     'และค่าคงที่แบรนด์ (กรม ทอง brand tag) เก็บไว้ที่เดียว '
                     '· เรียกจาก command line ดูค่าได้ด้วย (--list หรือระบุ key)'},
            {'name': 'ต่อ SegmentProfile เข้า skill auto-diagram-generator', 'status': DONE,
             'note': 'เพิ่ม input `segment:` เป็น field บังคับ และ Step 1.5 ดึงสไตล์ก่อนวาด '
                     '· corner_radius / stroke_width / accent / prefer_type มาจากโปรไฟล์แล้ว '
                     '· เพิ่ม anti-pattern 4 ข้อ กันเอาสีรองไปใช้แทนสีแบรนด์'},
            {'name': 'ต่อ SegmentProfile เข้า skill flux-cover-image', 'status': DONE,
             'note': '**เลิกรับ pose_category กับ background_mood เป็น input แล้ว** '
                     'ดึงจาก segment แทน · prompt พื้นหลังประกอบจาก cover_prompt() '
                     'ไม่ให้เขียนเอง · ยังคงกฎเดิมที่ท่าต้องล้อกับ hook — ถ้าขัดกันให้ทักผู้ใช้ '
                     '· มี pose_override สำหรับกรณีพิเศษ แต่ต้องบอกเหตุผล'},
            {'name': 'ชี้ agent นักเขียน 6 ตัวและ Graphic Designer ให้อ่าน SegmentProfile',
             'status': DONE,
             'note': 'เพิ่มบล็อกท้ายไฟล์ 7 agent (19-24 + 25) ไม่ได้เขียน agent ใหม่ '
                     '· กันไม่ให้ต้องก๊อปโปรไฟล์ซ้ำ 6 ไฟล์แล้วเพี้ยนกันทีหลัง '
                     '· กติกาที่ใส่ไว้: ถ้าโปรไฟล์ขัดกับไฟล์ agent ให้ยึดโปรไฟล์แล้วรายงาน '
                     'และนักเขียนต้องส่ง `segment:` ต่อให้ Graphic Designer เสมอ'},

            # --- จาก ai-marketing-skills: Expert Panel + Humanizer ---
            {'name': 'รายการคำและรูปประโยค AI-slop ภาษาไทย แก้ไขได้จากหน้าจอ', 'status': TODO,
             'note': 'ที่มา: content-ops/experts/humanizer.md (24 pattern + 45 คำต้องห้าม) '
                     'แต่เป็นภาษาอังกฤษล้วน ใช้กับบทความไทยไม่ได้เลย ต้องรวบรวมเอง '
                     'เช่น "ในยุคดิจิทัลที่..." "อย่างมีประสิทธิภาพ" "ครบวงจร" '
                     '"ตอบโจทย์ทุกความต้องการ" · ต้องค่อยๆ สะสมจากของจริง'},
            {'name': 'skill expert-panel-th — ประกอบคณะกรรมการ ให้คะแนน วนจนถึง 90', 'status': TODO,
             'note': 'ที่มา: content-ops/SKILL.md · คณะกรรมการ 7-10 คนตามประเภทงาน '
                     'ถ่วงน้ำหนักตัวตรวจ AI-slop 1.5 เท่า วนแก้สูงสุด 3 รอบ '
                     '· ต้องลบ preamble telemetry ของเขาออกก่อนใช้'},
            {'name': 'เกณฑ์ให้คะแนน 5 ชุด (บทความ / กลยุทธ์ / หน้าขาย / ภาพ / ประเมิน)', 'status': TODO,
             'note': 'ที่มา: content-ops/scoring-rubrics/ — แปลและปรับให้เข้ากับตลาดไทย'},
            {'name': 'เก็บคะแนนลง DB — ContentScore และ ExpertScore ผูกกับบทความ', 'status': TODO,
             'note': 'เก็บทุกรอบไม่ใช่แค่รอบสุดท้าย เพราะเส้นทางการแก้คือของมีค่า'},
            {'name': 'หน้า /owner/content-quality/ และหน้ารายละเอียดคะแนน', 'status': TODO,
             'note': 'คลิกทั้งแถว ไม่ใส่คอลัมน์ปุ่ม · ต้องผ่าน Frontend Designer ก่อน'},
            {'name': 'ประตูอนุมัติ — บทความจะเผยแพร่ได้ต้องมีคะแนนผ่านและเจ้าของกดอนุมัติ',
             'status': TODO,
             'note': 'ทำให้กฎ "publish เป็น draft เสมอ" ที่ตอนนี้เป็นแค่ข้อตกลงในไฟล์ memory '
                     'กลายเป็นสถานะใน DB ที่ agent ข้ามไม่ได้'},

            # --- ไอเดียที่ 2 และ 3 จาก AI-Content-Studio ---
            {'name': 'manifest ต่อบทความ — รันซ้ำแล้วข้ามขั้นที่ทำเสร็จแล้ว', 'status': TODO,
             'note': 'ที่มา: PIPELINE_STEPS + start_point ใน AI-Content-Studio/pipeline.py '
                     '· แก้ปัญหาบทความพังกลางทางแล้วต้องเริ่มใหม่ทั้งหมด'},
            {'name': 'จุดหยุดให้อนุมัติ prompt ก่อนสร้างภาพจริง', 'status': TODO,
             'note': 'ที่มา: HITL checkpoint ใน AI-Content-Studio/agents.py '
                     '· ให้ดูและแก้ prompt ของ diagram ทุกหัวข้อก่อนยิง FLUX '
                     'ประหยัดโควตา HuggingFace เพราะแก้ก่อนเผา ไม่ใช่ดูรูปเสร็จแล้วสั่งทำใหม่'},
        ],
    },
]


# ---------------------------------------------------------------------------
# เรื่องที่ติดรอเจ้าของตัดสินใจ — ขึ้นกล่องแดงพร้อมนับวันที่ค้าง
# ปิดแล้วอย่าลบ ให้ย้ายไปเป็นคอมเมนต์ท้ายรายการเพื่อให้ตามรอยได้
# ---------------------------------------------------------------------------
#
# ปิดไปแล้ว (เก็บไว้ให้ตามรอยได้ว่าตัดสินใจว่าอะไรและเมื่อไหร่):
#   RM-1  ยืนยันสถานะเฟส 1-6 ที่บันทึกย้อนหลัง → เจ้าของยืนยัน 26 ส.ค. 2569 ว่า "ตรง"
#         สถานะเฟส 1-6 จึงถือเป็นความจริงตั้งแต่วันนั้น ไม่ต้องทวนอีก
#   RM-2  จะทำอย่างไรกับงานค้างในปฏิทิน 162 รายการ → เจ้าของเลือก 26 ส.ค. 2569
#         "ปิดเป็นกลุ่ม เก็บของที่ยังจริง" · ปิดไป 88 รายการ เหลือค้าง 74
DECISIONS = [
    {'code': 'RM-3',
     'topic': 'งานจริง 29 รายการที่เลยกำหนดแต่ไม่มีในแผน จะเอาไปไว้ไหน',
     'detail': 'หลังสะสางปฏิทินตามมติ RM-2 ยังเหลืองานที่เป็นงานจริง ไม่ใช่พิธีกรรม '
               'และไม่ใช่แผน 60 วัน อีก 29 รายการที่เลยกำหนดแล้ว '
               'เช่น "Admin CRUD ทุกส่วนของลูกค้า" "About page redesign" '
               '"Email Sequence 5 ฉบับ" "Pillar Pages 4 หน้า" "Lead Magnet: AI Readiness Checklist" '
               '· ตามกติกาข้อ 3 ของไฟล์นี้ งานที่ไม่มีในแผน = งานนอกแผน '
               '· ทางเลือก: (ก) เอาเข้าเป็นเฟส 9 งานการตลาดและการขาย '
               '(ข) กระจายเข้าเฟสที่มีอยู่ (ค) ปิดทิ้งเพราะไม่ทำแล้ว',
     'since': date(2026, 8, 26)},
    {'code': 'QF-1',
     'topic': 'จะใช้หน้าขาย QueueFlow เวอร์ชันไหนเป็นตัวจริง',
     'detail': 'ทำไว้ 4 เวอร์ชัน (V1-V4) ยังไม่มีมติ · ปล่อยไว้ต้องดูแลซ้ำซ้อน 4 ไฟล์ '
               'และวัดผล A/B ไม่ได้เพราะไม่มีใครรู้ว่าตัวไหนคือตัวหลัก',
     'since': date(2026, 7, 3)},
    {'code': 'QF-2',
     'topic': 'ค่าติดตั้ง ฿9,900-39,900 จะเก็บต่อหรือถอด',
     'detail': 'Agent #26 escalate ไว้ตั้งแต่ 3 ก.ค. 69 — คู่แข่งไทยแทบไม่มี setup fee '
               'ทำให้เราปิดดีลยากกว่าโดยไม่จำเป็น · ต้องเคาะก่อนเริ่มขายจริง',
     'since': date(2026, 7, 3)},
    {'code': 'PY-1',
     'topic': 'ระบบ Series/EP บนเว็บ จะสร้าง model ใหม่หรือใช้ tag',
     'detail': 'คอร์ส Python 101 มี 5 ตอนแล้วแต่คนเรียนหาตอนถัดไปเองไม่ได้ '
               'ไม่มีปุ่มก่อนหน้า/ถัดไป ไม่มีหน้าสารบัญคอร์ส',
     'since': date(2026, 8, 16)},
]


# ---------------------------------------------------------------------------
# หนี้ทางเทคนิค — รู้อยู่ว่าไม่สวย แต่จงใจยังไม่แก้ ต้องบอกเหตุผลเสมอ
# ---------------------------------------------------------------------------
TECH_DEBT = [
    {'topic': 'งานจำนวนมากยังไม่ถูก commit',
     'why': 'ตอนนี้มีไฟล์แก้ไข 15 ไฟล์และไฟล์ใหม่อีกหลายสิบไฟล์ค้างใน working tree '
            'รวมถึงระบบ Project Monitor ทั้งชุด · ถ้าเครื่องพังตอนนี้งานหายทั้งหมด '
            '· ยังไม่ commit เพราะกฎห้าม push จนกว่าเจ้าของจะสั่ง แต่ commit ทำได้',
     'owner': 'ai-orchestrator'},
    {'topic': 'memory file บอกว่า Project Monitor ยังไม่ implement ทั้งที่ทำไปแล้ว',
     'why': 'project_monitor_system.md เขียนว่า "ยังไม่ implement" ลงวันที่ 20 ส.ค. '
            'แต่โค้ดกับ migration เสร็จแล้ว · เป็นตัวอย่างว่าทำไมต้องมีแผนที่บังคับให้อัปเดต '
            '· ต้องแก้ memory file ให้ตรงหลังเจ้าของยืนยันสถานะ',
     'owner': 'chief-of-staff'},
    {'topic': 'หัวข้อในปฏิทินมี emoji ทั้งที่ตกลงกันว่าห้าม',
     'why': 'กติกา feedback_calendar_no_emoji ห้ามใส่ emoji ใน title ของ CalendarEvent '
            'แต่ของเก่าที่สร้างไว้ก่อนกติกายังมีอยู่หลายสิบรายการ '
            '· รอสะสางพร้อมกันตอนเคลียร์งานค้าง (มติ RM-2)',
     'owner': 'chief-of-staff'},
    {'topic': 'ไฟล์รูปและ screenshot กระจัดกระจายที่ root ของโปรเจกต์',
     'why': 'มีไฟล์ .jpg .png .avif หลายไฟล์วางอยู่ที่ root ไม่ได้อยู่ใน media/ หรือ static/ '
            '· ไม่กระทบการทำงาน แต่ทำให้ git status รกจนมองไม่เห็นของสำคัญ',
     'owner': 'ai-orchestrator'},
]


# ---------------------------------------------------------------------------
# ฟังก์ชันช่วยคำนวณ — หน้าเว็บเรียกใช้จากที่นี่ที่เดียว
# ---------------------------------------------------------------------------
def build_phases(metrics=None, calendar_hits=None):
    """คืนรายการเฟสพร้อมความคืบหน้า ตัวเลขจริงจาก DB และงานในปฏิทินที่จับคู่ได้

    metrics       — dict ตัวเลขจริงจากฐานข้อมูล ณ เวลาที่เปิดหน้า
    calendar_hits — dict {คำค้น: {'total': n, 'done': n}} จากตาราง CalendarEvent
    """
    metrics = metrics or {}
    calendar_hits = calendar_hits or {}
    result = []
    for phase in PHASES:
        items = phase['items']
        done = sum(1 for item in items if item['status'] in COMPLETED_STATUSES)
        blocked = sum(1 for item in items if item['status'] == BLOCKED)
        result.append({
            **phase,
            'items': [
                {**item,
                 'meta': STATUS_META[item['status']],
                 'calendar_hit': calendar_hits.get(item.get('calendar')) if item.get('calendar') else None}
                for item in items
            ],
            'meta': STATUS_META[phase['status']],
            'done_count': done,
            'blocked_count': blocked,
            'total_count': len(items),
            'remaining_count': len(items) - done,
            # เฟสที่ปิดไปแล้วแต่มีคนเติมงานใหม่เข้ามาทีหลัง ต้องไม่ขึ้นป้ายเขียวเฉยๆ
            # ไม่งั้นแผนจะโกหกทั้งที่ข้อมูลข้างในถูกต้อง
            'reopened': phase['status'] == DONE and done < len(items),
            'percent': round(done * 100 / len(items)) if items else 0,
            'metrics': [
                {'label': m['label'], 'value': metrics.get(m['key'], 0)}
                for m in phase.get('metrics', [])
            ],
        })
    return result


def overall_progress():
    """ความคืบหน้ารวมทั้งโปรเจกต์ นับเป็นจำนวนเรื่อง ไม่ใช่จำนวนเฟส"""
    items = [item for phase in PHASES for item in phase['items']]
    done = sum(1 for item in items if item['status'] in COMPLETED_STATUSES)
    blocked = sum(1 for item in items if item['status'] == BLOCKED)
    return {
        'done': done,
        'total': len(items),
        'remaining': len(items) - done,
        'blocked': blocked,
        'phases': len(PHASES),
        'phases_done': sum(1 for p in PHASES if p['status'] in COMPLETED_STATUSES),
        'percent': round(done * 100 / len(items)) if items else 0,
    }


def current_phase():
    """เฟสที่ระบุไว้ใน CURRENT — ใช้แสดงชื่อเฟสบนแถบบนสุด"""
    for phase in PHASES:
        if phase['no'] == CURRENT['phase']:
            return phase
    return None


def calendar_keywords():
    """คำค้นทั้งหมดที่ item ในแผนประกาศไว้ — view เอาไปยิงหา CalendarEvent"""
    return [item['calendar'] for phase in PHASES for item in phase['items']
            if item.get('calendar')]


def open_decisions(today):
    """เรื่องที่ยังค้างรอตัดสินใจ พร้อมจำนวนวันที่ค้าง"""
    return [{**d, 'days': (today - d['since']).days} for d in DECISIONS]


# ---------------------------------------------------------------------------
# แผนนี้ถูกแก้ครั้งล่าสุดเมื่อไหร่ — ใช้เตือนว่าโค้ดเดินไปแต่แผนไม่ขยับ
# ---------------------------------------------------------------------------
STALE_AFTER_DAYS = 7

# ถามจาก git ก่อนเพราะได้วันที่ "แก้เนื้อหาจริง" ไม่ใช่วันที่ไฟล์ถูกก๊อปลงเครื่อง
# ถ้าไม่มี git (เช่นบนเครื่องจริงที่ deploy ด้วยการคัดลอกไฟล์) ค่อยถอยไปใช้เวลาแก้ไฟล์
def last_updated():
    """วันที่แก้ไฟล์นี้ล่าสุด คืน None ถ้าหาไม่ได้จริงๆ (ต้องไม่ทำให้หน้าเว็บพัง)"""
    import os
    import subprocess
    from datetime import datetime

    path = os.path.abspath(__file__)
    try:
        stamp = subprocess.run(
            ['git', 'log', '-1', '--format=%cI', '--', path],
            cwd=os.path.dirname(path), capture_output=True, text=True, timeout=5,
        ).stdout.strip()
        if stamp:
            return datetime.fromisoformat(stamp).date()
    except (OSError, ValueError, subprocess.SubprocessError):
        pass

    try:
        return datetime.fromtimestamp(os.path.getmtime(path)).date()
    except OSError:
        return None


def staleness(today):
    """สรุปว่าแผนนี้เก่าไปหรือยัง สำหรับแสดงแถบเตือนบนหน้า roadmap"""
    updated = last_updated()
    if updated is None:
        return {'known': False, 'days': None, 'is_stale': False, 'updated': None}
    days = (today - updated).days
    return {
        'known': True,
        'updated': updated,
        'days': days,
        'is_stale': days > STALE_AFTER_DAYS,
        'limit': STALE_AFTER_DAYS,
    }
