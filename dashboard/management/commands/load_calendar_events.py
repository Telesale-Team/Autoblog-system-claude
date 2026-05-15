"""
Management command: load_calendar_events
โหลด system events ทั้งหมด (milestones + recurring) เข้า CalendarEvent DB

Usage:
    python manage.py load_calendar_events           # load ทั้งหมด
    python manage.py load_calendar_events --clear   # ลบของเดิมก่อน แล้ว load ใหม่
"""
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import CalendarEvent


MILESTONES = [
    # ═══ 60-DAY ACTION PLAN ═══════════════════════════════════════════════

    # Phase 1: Setup (Day 1-7)
    ("2026-05-15", "⚙️ [Day 1] ติดตั้ง Infrastructure",            "action",   "Node.js 24, API key จาก Anthropic, VPS $6/เดือน DigitalOcean, ngrok สำหรับ testing — ทดสอบ localhost ก่อน deploy"),
    ("2026-05-16", "📱 [Day 2] สร้าง LINE Official Account",        "action",   "Enable Messaging API + ดึง Channel Access Token + Channel Secret — บันทึกใน .env"),
    ("2026-05-17", "🔗 [Day 3] เชื่อม LINE → OpenClaw",             "action",   "ตั้ง webhook URL + ทดสอบ LINE echo bot พื้นฐาน — ยืนยัน Channel Access Token ใช้งานได้"),
    ("2026-05-18", "🤖 [Day 4] เขียน System Prompt + 20+ FAQ",      "action",   "ออกแบบ AI persona + สร้าง knowledge base ครอบคลุม 20+ FAQ — ทดสอบ tone และความถูกต้องของคำตอบ"),
    ("2026-05-19", "🖥️ [Day 5] Deploy บน VPS ($6/เดือน)",           "action",   "DigitalOcean Droplet $6/เดือน + ติดตั้ง Node.js + PM2 + ตั้ง reverse proxy — live demo server running"),
    ("2026-05-21", "✅ [Day 7] Demo Production-Ready",               "milestone","ทดสอบ 20+ scenarios ครบ + response time < 3 วินาที + no hallucination — Gate 1 ผ่าน"),

    # Phase 2: Demo Creation (Day 8-14)
    ("2026-05-22", "🎬 [Day 8] สร้าง Demo 3 แบบ",                   "action",   "3 demo scenarios: (1) E-commerce FAQ 20+ คำถาม (2) Clinic appointment booking (3) Hotel booking + FAQ — แต่ละ demo มี 20+ FAQ"),
    ("2026-05-24", "📹 [Day 10] ถ่าย Video Demo 60 วินาที",          "action",   "Thai voiceover + CapCut editing — สาธิต conversation จริง ไม่ใช่ slides — highest conversion format สำหรับ SME"),
    ("2026-05-25", "📄 [Day 11] สร้าง Sales Materials",              "action",   "ครบชุด: (1) One-pager A4 (2) Proposal template พร้อม pricing (3) Invoice template (4) Service agreement + NDA — ทุกอย่าง editable"),
    ("2026-05-27", "🌐 [Day 13] ตั้ง LinkedIn + Facebook + Salepage","action",   "LinkedIn Company Page + Facebook Page + Salepage (Netlify/GitHub Pages) — กรอก bio, portfolio, contact, pricing"),
    ("2026-05-28", "✅ [Day 14] Sales Materials ครบ",                "milestone","Demo video + Sales Kit (one-pager, proposal, invoice, service agreement) + Online presence — Gate 2 ผ่าน"),

    # Phase 3: Outreach (Day 15-28)
    ("2026-05-29", "📢 [Day 15] Publish Content ชุดแรก",             "action",   "LinkedIn post + video, FB post, TikTok — 3 platforms พร้อมกัน — เน้น pain point ลูกค้าและ ROI จริง"),
    ("2026-05-31", "📋 [Day 17] สร้าง Prospect List 100 ราย",        "action",   "50 คลินิก + 50 e-commerce shops ใน Google Sheets CRM — คอลัมน์: ชื่อ, เจ้าของ, LINE/FB, สถานะ, วันติดต่อ — DM script พร้อม"),
    ("2026-06-02", "💬 [Day 19] ส่ง Cold Message 30 ราย",            "action",   "Personalized DM Facebook/LINE — mention ชื่อธุรกิจจริง + pain point เฉพาะ industry — expect 10-20% reply rate (3-6 replies)"),
    ("2026-06-04", "👥 [Day 22] Join 3 Facebook Groups",             "action",   "SME Thailand + e-commerce Thailand + คลินิก/สาธารณสุข — ตอบคำถาม 2-3 ครั้ง/วัน เพื่อ build authority ก่อน pitch"),
    ("2026-06-08", "📞 [Day 25] Discovery Calls 3+ ราย",             "milestone","คุยกับ prospect ที่สนใจ — ถาม pain point + budget + timeline — เป้า qualify 2 ในนั้นเพื่อ demo"),
    ("2026-06-11", "✅ [Day 28] 3+ Discovery Calls Done",            "milestone","Pipeline มี qualified leads พร้อม demo — เริ่ม Phase 4: ส่ง proposal + ปิดดีล"),

    # Phase 4: Close (Day 29-38)
    ("2026-06-12", "🎯 [Day 29] Demo Calls + ส่ง Proposal",          "action",   "Demo 30 นาที + ตอบ objection + ส่ง Proposal deck (pricing + scope + timeline) ให้ 1-2 hot leads — ใช้ HelloSign สำหรับ e-signature"),
    ("2026-06-16", "🤝 [Day 33] รับ Deposit ฿10,000!",               "milestone","50% setup fee = ฿10,000 — Project greenlit, onboarding checklist ส่งลูกค้า, เริ่มนัด kick-off call"),
    ("2026-06-21", "✍️ [Day 38] Contract Signed",                    "milestone","Service Agreement + NDA signed via HelloSign + ฿10K received — Gate 4 ผ่าน, เริ่ม delivery"),

    # Phase 5: Delivery (Day 39-52)
    ("2026-06-22", "🔧 [Day 39] เริ่ม Customize ระบบ",               "action",   "Kick-off call: รวบรวม FAQ จริง + brand voice + escalation rules + hours of operation — migrate ข้อมูลเข้า knowledge base"),
    ("2026-06-26", "🚀 [Day 44] Deploy บน Customer VPS",             "action",   "ตั้ง VPS ให้ลูกค้า + configure LINE OA + ทดสอบ webhook + integration ทุกตัว — staging → production"),
    ("2026-07-01", "🧪 [Day 47] User Acceptance Testing",            "action",   "ลูกค้า test 3 วัน — รวบรวม feedback → แก้ bug + ปรับ tone + เพิ่ม FAQ ที่ขาด — max 2 revision rounds"),
    ("2026-07-03", "📚 [Day 48] Training ทีมลูกค้า",                 "action",   "สอน Dashboard: ดู chat log + อัปเดต FAQ + ตั้ง escalation → LINE agent + แนะนำ monitoring — ส่งคู่มือ PDF"),
    ("2026-07-05", "🟢 [Day 52] GO LIVE!",                           "milestone","ระบบ production running + 48h close monitoring + hotline support — Gate 5 ผ่าน"),

    # Phase 6: Get Paid (Day 53-60)
    ("2026-07-06", "🧾 [Day 53] ส่ง Invoice #2 ฿10,000",             "action",   "Invoice #2 ฿10,000 (final 50%) ส่งทันทีหลัง go-live — setup รวม ฿20,000 ครบ + ตั้ง recurring invoice MRR ฿3,000/เดือน"),
    ("2026-07-08", "💰 [Day 55] รับเงินครบ + MRR เริ่ม!",            "milestone","Setup รวม ฿20,000 + MRR ฿3,000/เดือน เริ่มนับ — ตั้ง auto-invoice รายเดือนใน system"),
    ("2026-07-09", "📊 [Day 56] สร้าง Case Study",                   "action",   "วัด metrics จริง: response rate, FAQ coverage, จำนวน conversations — เขียน case study + ขอ testimonial → โพส LinkedIn"),
    ("2026-07-13", "🔄 [Day 60] เริ่ม Cycle 2",                      "milestone","Follow-up pipeline ที่ยังค้างอยู่ + ขอ referral จากลูกค้าปัจจุบัน + target ปิดดีล #2 ภายใน Day 90"),

    # ═══ PRODUCT ROADMAP 6 เดือน ════════════════════════════════════════
    ("2026-05-15", "🏁 Sprint 1-3 Dashboard Complete",               "milestone","Dashboard, Pipeline, Revenue, Analytics, Backlog ครบ — พร้อมใช้งานจริง"),
    ("2026-05-29", "🚀 LINE AI Pro — Launch!",                       "milestone","Setup ฿20,000 | MRR ฿3,000/เดือน | Deliver 1-2 สัปดาห์ | Margin ~70% | Target: ร้านค้าออนไลน์, SME ทั่วไป | จุดขาย: Gen AI จริง vs rule-based, self-hosted, จ่ายครั้งเดียว"),
    ("2026-06-30", "🎯 เป้าปิด 2-3 ดีลแรก",                         "milestone","Month 2 target — MRR เริ่มนับ + สร้าง 1 Case Study พร้อมตัวเลข ROI จริง"),
    ("2026-07-15", "🏥 Private AI Clinic — Launch!",                 "milestone","Setup ฿80,000 | MRR ฿8,000/เดือน | Deliver 3-4 สัปดาห์ | Target: คลินิก 30,000+ แห่งในไทย | PDPA-proof: Ollama on-premise, zero data egress"),
    ("2026-07-15", "📡 Omni AI Agent — Launch!",                     "milestone","Setup ฿50,000 | MRR ฿6,000/เดือน | LINE+FB+IG+TikTok+WebChat ใน gateway เดียว | Target: โรงแรม, ธุรกิจ multi-channel"),
    ("2026-08-15", "🎯 เป้า MRR ฿20,000/เดือน",                      "milestone","Month 4 revenue target — 3 partners acquired + 2 case studies พร้อม"),
    ("2026-09-01", "🔄 Quarterly Planning Q3",                       "recurring","2-day strategy session — ทบทวน MRR + product mix + channels + เพิ่ม agent ตาม revenue milestone"),
    ("2026-09-15", "⚙️ AI Workflow Bot — Launch!",                   "milestone","Setup ฿35,000 | MRR ฿4,500/เดือน | Daily reports 08:00, stock alerts, CRM update, lead follow-up, social monitoring"),
    ("2026-09-15", "👥 Team AI Assistant — Launch!",                 "milestone","Setup ฿40,000 | MRR ฿5,000/เดือน | ประหยัด 20-30 นาที/คน/วัน | ทีม 20 คน = 400+ ชม./เดือน | Slack/Teams/LINE"),
    ("2026-10-01", "📈 Google Ads เริ่ม (฿5K-15K/เดือน)",            "action",   "High-intent keywords: 'AI chatbot ร้านอาหาร', 'LINE chatbot ราคา' — เริ่มหลัง case study พร้อม เพื่อเพิ่ม conversion rate"),
    ("2026-10-01", "💬 [Feature] Chat กับ Agent จาก Dashboard",      "action",   "Integrate Anthropic API → กดที่ agent card ส่งคำสั่งได้เลย — ไม่ต้องออกไปหน้าอื่น"),
    ("2026-10-15", "🎯 เป้า MRR ฿50,000/เดือน",                      "milestone","Month 6 target: 15+ customers | 5 case studies | 5 partners | พร้อม activate Data Analyst + Customer Success agents"),
    ("2026-10-15", "🏆 Activate Data Analyst + Customer Success",    "milestone","MRR ฿50K+ → เพิ่ม agents ตาม revenue milestone — Data Analyst วิเคราะห์ churn + Customer Success ดูแล retention"),

    # ═══ MARKETING MILESTONES ════════════════════════════════════════════
    ("2026-06-01", "📋 Lead Magnet: AI Readiness Checklist",         "action",   "สร้าง PDF 'AI Readiness Checklist 10 ข้อสำหรับ SME ไทย' + ฝัง Email Form ใน Blog (Mailchimp free tier 500 contacts) + CTA block ทุกบทความ + Thank You page"),
    ("2026-06-15", "📧 Email Sequence 5 ฉบับ",                        "action",   "Day 0: ส่ง Checklist + แนะนำตัว | Day 2: Case study ธุรกิจคล้ายกัน | Day 4: 3 สัญญาณต้องเริ่มใช้ AI | Day 7: FAQ ราคา/เวลา/ความยุ่งยาก | Day 10: CTA 'ขอ AI Audit ฟรี 30 นาที'"),
    ("2026-06-20", "📅 ตั้ง Calendly สำหรับ Free AI Audit",           "action",   "Free tier + link ในบทความและ email signature + เป้า 2 calls/เดือน Month 1 — เพิ่มเป็น 8 calls/เดือน Month 3"),
    ("2026-07-01", "🏛️ Pillar Pages 4 หน้า",                         "action",   "P1: AI สำหรับ SME ไทยคืออะไร | P2: ระบบ AI ที่ SME ต้องมี | P3: เครื่องมือ AI เปรียบเทียบ | P4: ROI & ราคา AI สำหรับ SME — แต่ละหน้า 2,000+ คำ"),

    # ═══ KPI MILESTONES ══════════════════════════════════════════════════
    ("2026-06-30", "📊 KPI Check: เดือน 1",                           "milestone","เป้า: บทความ publish 2/สัปดาห์ | MQL 10 leads | Free Audit 2 calls | ดีลปิด 1 | MRR ฿0→start"),
    ("2026-09-30", "📊 KPI Check: เดือน 3",                           "milestone","เป้า: MQL สะสม 50 leads | Free Audit 8 calls/เดือน | ดีลปิด 3 | MRR ฿30,000"),
]

CATEGORY_COLOR = {
    "milestone": "#c9a96e",
    "action":    "#b8924f",
    "recurring": "#6c757d",
    "content":   "#1a2744",
}


def _generate_recurring(weeks=26):
    """สร้าง recurring events 26 สัปดาห์ (~6 เดือน) จากวันนี้"""
    events = []
    today = date.today()
    # Monday ของสัปดาห์นี้
    base_monday = today - timedelta(days=today.weekday())

    for w in range(weeks):
        monday = base_monday + timedelta(weeks=w)
        friday = monday + timedelta(days=4)

        events.append((
            monday.isoformat(),
            "☀️ Daily Stand-up",
            "recurring",
            "Daily 09:00 — แต่ละ agent ส่ง stand-up",
        ))
        events.append((
            friday.isoformat(),
            "📊 Weekly Review",
            "recurring",
            "ทุกศุกร์ 17:00 — CEO + CoS + 3 agents",
        ))

    # Monthly review ทุกวันที่ 1 ของเดือน ไป 6 เดือน
    for m in range(6):
        target = (today + timedelta(days=30 * m)).replace(day=1)
        events.append((
            target.isoformat(),
            "📅 Monthly Review",
            "recurring",
            "Monthly Business Review — all agents",
        ))

    return events


class Command(BaseCommand):
    help = "โหลด system calendar events (milestones + recurring) เข้า DB"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="ลบ system events เดิมก่อนแล้ว load ใหม่",
        )

    def handle(self, *args, **options):
        from datetime import datetime
        from django.utils.dateparse import parse_date

        if options["clear"]:
            deleted, _ = CalendarEvent.objects.filter(is_system=True).delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing system events"))

        all_events = MILESTONES + _generate_recurring(weeks=26)
        created = 0

        for start_str, title, category, description in all_events:
            start_dt = parse_date(start_str)
            if not start_dt:
                continue

            exists = CalendarEvent.objects.filter(
                title=title,
                start_datetime__date=start_dt,
                is_system=True,
            ).exists()
            if exists:
                continue

            from django.utils import timezone as tz
            naive_dt = datetime(start_dt.year, start_dt.month, start_dt.day, 0, 0, 0)
            CalendarEvent.objects.create(
                title=title,
                start_datetime=tz.make_aware(naive_dt),
                all_day=True,
                category=category,
                description=description,
                color=CATEGORY_COLOR.get(category, "#c9a96e"),
                is_system=True,
                created_by=None,
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f"OK: created {created} system events in DB"
        ))
        self.stdout.write(f"   Milestones: {len(MILESTONES)}")
        self.stdout.write(f"   Recurring:  {len(all_events) - len(MILESTONES)}")
