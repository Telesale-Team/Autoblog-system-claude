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
    ("2026-05-15", "⚙️ [Day 1] ติดตั้ง Infrastructure",            "action",   "Install Node.js 24, OpenClaw, test localhost:18789"),
    ("2026-05-16", "📱 [Day 2] สร้าง LINE Official Account",        "action",   "Enable Messaging API + credentials"),
    ("2026-05-17", "🔗 [Day 3] เชื่อม LINE → OpenClaw",             "action",   "Channel Access Token + webhook"),
    ("2026-05-18", "🤖 [Day 4] เขียน System Prompt + 20+ FAQ",      "action",   "AI persona + knowledge base พร้อม"),
    ("2026-05-19", "🖥️ [Day 5] Deploy บน VPS ($6/เดือน)",           "action",   "DigitalOcean VPS + live demo server running"),
    ("2026-05-21", "✅ [Day 7] Demo Production-Ready",               "milestone","ทดสอบ 20+ scenarios ครบ — Gate 1 ผ่าน"),

    # Phase 2: Demo Creation (Day 8-14)
    ("2026-05-22", "🎬 [Day 8] สร้าง Demo 3 แบบ",                   "action",   "E-commerce / Clinic / Hotel — 20+ FAQ each"),
    ("2026-05-24", "📹 [Day 10] ถ่าย Video Demo 60 วินาที",          "action",   "Thai voiceover + CapCut — highest conversion format"),
    ("2026-05-25", "📄 [Day 11] สร้าง Sales Materials",              "action",   "One-pager + Proposal template + Invoice + Service agreement"),
    ("2026-05-27", "🌐 [Day 13] ตั้ง LinkedIn + Facebook + Salepage","action",   "Online presence พร้อม — Netlify / GitHub Pages"),
    ("2026-05-28", "✅ [Day 14] Sales Materials ครบ",                "milestone","Demo + Content + Sales Kit — Gate 2 ผ่าน"),

    # Phase 3: Outreach (Day 15-28)
    ("2026-05-29", "📢 [Day 15] Publish Content ชุดแรก",             "action",   "LinkedIn post + video, FB post, TikTok — 3 platforms"),
    ("2026-05-31", "📋 [Day 17] สร้าง Prospect List 100 ราย",        "action",   "50 คลินิก + 50 e-commerce shops → Google Sheets CRM"),
    ("2026-06-02", "💬 [Day 19] ส่ง Cold Message 30 ราย",            "action",   "Personalized DM Facebook/LINE — expect 10-20 replies"),
    ("2026-06-04", "👥 [Day 22] Join 3 Facebook Groups",             "action",   "SME / e-commerce / clinics — answer questions, build authority"),
    ("2026-06-08", "📞 [Day 25] Discovery Calls 3+ ราย",             "milestone","คุยกับ prospect ที่สนใจ — Gate 3 target"),
    ("2026-06-11", "✅ [Day 28] 3+ Discovery Calls Done",            "milestone","Pipeline มี qualified leads — เริ่ม Phase 4"),

    # Phase 4: Close (Day 29-38)
    ("2026-06-12", "🎯 [Day 29] Demo Calls + ส่ง Proposal",          "action",   "ส่ง proposal ให้ 1-2 hot leads"),
    ("2026-06-16", "🤝 [Day 33] รับ Deposit ฿10,000!",               "milestone","50% setup fee — Project greenlit, onboarding เริ่ม"),
    ("2026-06-21", "✍️ [Day 38] Contract Signed",                    "milestone","HelloSign + ฿10K received — Gate 4 ผ่าน"),

    # Phase 5: Delivery (Day 39-52)
    ("2026-06-22", "🔧 [Day 39] เริ่ม Customize ระบบ",               "action",   "Gather requirements + migrate FAQ + customize for customer"),
    ("2026-06-26", "🚀 [Day 44] Deploy บน Customer VPS",             "action",   "Configure OA + test all integrations"),
    ("2026-07-01", "🧪 [Day 47] User Acceptance Testing",            "action",   "Customer tests 3 วัน + feedback → fix issues"),
    ("2026-07-03", "📚 [Day 48] Training ทีมลูกค้า",                 "action",   "Dashboard + FAQ updates + escalation process"),
    ("2026-07-05", "🟢 [Day 52] GO LIVE!",                           "milestone","ระบบ production + 48h close monitoring — Gate 5 ผ่าน"),

    # Phase 6: Get Paid (Day 53-60)
    ("2026-07-06", "🧾 [Day 53] ส่ง Invoice #2 ฿10,000",             "action",   "Final payment immediately after go-live"),
    ("2026-07-08", "💰 [Day 55] รับเงินครบ + MRR เริ่ม!",            "milestone","Setup รวม ฿20,000 + MRR ฿3,000/เดือน เริ่มนับ"),
    ("2026-07-09", "📊 [Day 56] สร้าง Case Study",                   "action",   "Metrics + screenshots + testimonial → LinkedIn"),
    ("2026-07-13", "🔄 [Day 60] เริ่ม Cycle 2",                      "milestone","Follow-up pipeline + ขอ referral + target deal #2 by Day 90"),

    # ═══ PRODUCT ROADMAP 6 เดือน ════════════════════════════════════════
    ("2026-05-15", "🏁 Sprint 1-3 Dashboard Complete",               "milestone","Dashboard, Pipeline, Revenue, Analytics, Backlog ครบ"),
    ("2026-05-29", "🚀 LINE AI Pro — Launch!",                       "milestone","Product #1: Setup ฿20K | MRR ฿3K/เดือน | Delivery 1-2 สัปดาห์"),
    ("2026-06-30", "🎯 เป้าปิด 2-3 ดีลแรก",                         "milestone","Month 2 target — MRR เริ่มนับ + สร้าง 1 Case Study"),
    ("2026-07-15", "🏥 Private AI Clinic — Launch!",                 "milestone","Product #2: Setup ฿80K | MRR ฿8K | ตลาด 30,000+ คลินิก | PDPA-safe"),
    ("2026-07-15", "📡 Omni AI Agent — Launch!",                     "milestone","Product #3: Setup ฿50K | MRR ฿6K | LINE+FB+IG+TikTok"),
    ("2026-08-15", "🎯 เป้า MRR ฿20,000/เดือน",                      "milestone","Month 4 revenue target — 3 partners acquired"),
    ("2026-09-01", "🔄 Quarterly Planning Q3",                       "recurring","2-day strategy session — ทบทวน MRR + product mix + channels"),
    ("2026-09-15", "⚙️ AI Workflow Bot — Launch!",                   "milestone","Product #4: Setup ฿35K | MRR ฿4.5K | Daily reports + CRM + alerts"),
    ("2026-09-15", "👥 Team AI Assistant — Launch!",                 "milestone","Product #5: Setup ฿40K | MRR ฿5K | Slack/Teams/LINE"),
    ("2026-10-01", "📈 Google Ads เริ่ม (฿5K-15K/เดือน)",            "action",   "High-intent keywords — start after case study ready"),
    ("2026-10-01", "💬 [Feature] Chat กับ Agent จาก Dashboard",      "action",   "Integrate Anthropic API → กดที่ agent card ส่งคำสั่งได้เลย"),
    ("2026-10-15", "🎯 เป้า MRR ฿50,000/เดือน",                      "milestone","Month 6 target: 15+ customers | 5 case studies | 5 partners"),
    ("2026-10-15", "🏆 Activate Data Analyst + Customer Success",    "milestone","MRR ฿50K+ → เพิ่ม agents ตาม revenue milestone"),
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
