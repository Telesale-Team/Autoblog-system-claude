"""แผนการตลาด (Playbook) — แหล่งความจริงเดียวของงานการตลาดที่ต้องทำซ้ำทุกสัปดาห์

ไฟล์นี้เป็นคนละชนิดกับ dashboard/roadmap.py โดยตั้งใจ:
  roadmap.py  = แผนของโค้ด งานมีวัน DONE แล้วจบ ไม่ต้องทำซ้ำ
  playbook.py = แผนของพฤติกรรม งานไม่มีวันจบ วัดด้วย "ทำไปกี่ครั้ง / ได้ lead กี่ราย
                เทียบกับเป้ารายสัปดาห์" ไม่ใช่ DONE/TODO

เอาสองอย่างนี้มาปนกันแล้วเปอร์เซ็นต์ความคืบหน้าจะโกหก (เจ้าของทักท้วง 27 ส.ค. 2569)
หน้า /owner/playbook/ อ่านจากไฟล์นี้ที่เดียว (เห็นได้เฉพาะ superuser เหมือน roadmap)

กติกาการใช้งาน:
  1. ช่องทางที่ auto ตัวเลขจริงดึงจาก DB โดย view (dashboard.views.playbook_view) — ห้ามพิมพ์มือ
  2. ช่องทางที่ manual (ยังไม่มีที่บันทึกในระบบ) ให้แก้ `manual_status` ในไฟล์นี้ตรงๆ
     เมื่อทำแล้วในสัปดาห์นั้น — เหมือนหลักการเดียวกับ roadmap.py ข้อ "คนกำหนดสถานะ ไม่ใช่ระบบเดา"
  3. งานที่ไม่มีอยู่ในไฟล์นี้ = งานนอกแผน ต้องถามเจ้าของก่อนลงมือ (กติกาเดียวกับ roadmap.py)
  4. ห้ามลบ channel ที่เคยมี — ถ้าเลิกทำช่องทางไหน ให้ตั้ง cadence เป็น 'paused' พร้อม note ว่าทำไม

ที่มาของเนื้อหาตั้งต้น: docs/gtm_strategy.html และ docs/action_plan.html (พ.ค. 2569 — เอกสารตาย
ไม่มีสถานะ ผลคือ 8 ช่องทางทำจริง 0 ช่องทาง) และงานที่ตกลงกันแล้ว 27 ส.ค. 2569 ตามเฟส 9 ของ roadmap.py
"""

from datetime import date, timedelta

# ---------------------------------------------------------------------------
# สถานะเทียบเป้า — คำศัพท์ต้องต่างจาก roadmap.py (DONE/TODO) เพราะความหมายต่างกัน
# roadmap: navy=กำลังทำ / เขียว=เสร็จถาวร / เทา=ยังไม่เริ่ม
# playbook: เขียว=ถึงเป้า (รีเซ็ตทุกสัปดาห์) / ทอง=ทำได้บางส่วน / แดง=ยังไม่ทำเลย / เทา=แค่ติดตาม ไม่ตั้งเป้า
# ---------------------------------------------------------------------------
ON_TARGET   = 'on_target'    # ทำถึงเป้าสัปดาห์นี้แล้ว
PARTIAL     = 'partial'      # ทำแล้วบางส่วน ยังไม่ถึงเป้า
NOT_STARTED = 'not_started'  # ยังไม่ทำเลยสัปดาห์นี้
TRACKED     = 'tracked'      # แค่ติดตามตัวเลข ไม่มีเป้าตายตัว (เช่น ลง Expense)
DONE_ONCE   = 'done_once'    # งานครั้งเดียวจบ ทำแล้ว ไม่ต้องทำซ้ำ

STATUS_META = {
    ON_TARGET:   {'label': 'ถึงเป้าสัปดาห์นี้',   'badge': 'success', 'icon': 'bi bi-check-circle-fill'},
    PARTIAL:     {'label': 'ทำได้บางส่วน',        'badge': 'warning', 'icon': 'bi bi-dash-circle-fill'},
    NOT_STARTED: {'label': 'ยังไม่เริ่มสัปดาห์นี้', 'badge': 'danger',  'icon': 'bi bi-exclamation-circle-fill'},
    TRACKED:     {'label': 'ติดตามอยู่',           'badge': 'secondary', 'icon': 'bi bi-graph-up'},
    DONE_ONCE:   {'label': 'ทำแล้ว (ครั้งเดียวจบ)', 'badge': 'success', 'icon': 'bi bi-patch-check-fill'},
}

WEEKLY = 'weekly'
ONCE = 'once'   # งานครั้งเดียว ไม่รีเซ็ตทุกสัปดาห์ (เช่น ขอ testimonial)
PAUSED = 'paused'  # เลิกทำชั่วคราว ต้องมี note ว่าทำไม


# ---------------------------------------------------------------------------
# ช่องทาง/กิจกรรมการตลาด — เฟส 9 กลุ่ม ฉ. ของ roadmap.py (เจ้าของอนุมัติ 27 ส.ค. 2569)
#
# tracking: 'auto'   — view ดึงตัวเลขจริงจาก DB ใส่ metrics[metric_key] ทุกครั้งที่เปิดหน้า
#           'manual' — ยังไม่มีที่บันทึกในระบบ ต้องแก้ manual_status ในไฟล์นี้เอง
# ---------------------------------------------------------------------------
CHANNELS = [
    {
        'key': 'outbound_dm',
        'name': 'ทักร้านนวด/สปาโดยตรง (DM / โทร / walk-in)',
        'icon': 'bi bi-chat-dots',
        'cadence': WEEKLY,
        'target': 20,
        'unit': 'ราย/สัปดาห์',
        'tracking': 'manual',
        'manual_status': NOT_STARTED,
        'note': 'ที่มา: outreach kit `docs/queueflow_outreach_kit.md` · ยังไม่มีที่บันทึกในระบบ '
                'รอ "ปุ่มเพิ่ม Lead เอง" (roadmap.py เฟส 9 กลุ่ม ค.) ระหว่างนี้นับมือแล้วมาแก้ manual_status '
                'ในไฟล์นี้ทุกสัปดาห์ · 19 lead ที่มีอยู่ตอนนี้เป็นสแปมหมด อย่ารอฟอร์ม ต้องออกไปหาเอง',
    },
    {
        'key': 'fb_group_post',
        'name': 'โพสต์ Facebook Group (community, ไม่ขายตรง)',
        'icon': 'bi bi-facebook',
        'cadence': WEEKLY,
        'target': 3,
        'unit': 'โพสต์/สัปดาห์',
        'tracking': 'manual',
        'manual_status': NOT_STARTED,
        'note': 'ที่มา: gtm_strategy.html ช่องทาง Facebook Group 9 niche (ร้านนวด/SME/คลินิก ฯลฯ) '
                'เขียนโดย facebook-group-writer · ยังไม่มีที่บันทึกในระบบ แก้ manual_status เองทุกสัปดาห์',
    },
    {
        'key': 'seo_article',
        'name': 'บทความ SEO ใหม่',
        'icon': 'bi bi-file-earmark-text',
        'cadence': WEEKLY,
        'target': 2,
        'unit': 'บทความ/สัปดาห์',
        'tracking': 'auto',
        'metric_key': 'seo_article',
        'note': 'ที่มา: gtm_strategy.html "Blog SEO 10 บทความ/เดือน" (~2.5/สัปดาห์ ปัดลงเป็น 2) '
                'นับจาก blog.Article ที่สร้างในสัปดาห์นี้ทุกสถานะ ไม่ใช่แค่ published',
    },
    {
        'key': 'lead_follow_up',
        'name': 'ตามงาน lead ค้าง (ทักซ้ำ / เปลี่ยนสถานะ)',
        'icon': 'bi bi-arrow-repeat',
        'cadence': WEEKLY,
        'target': None,  # dynamic — view คำนวณจากจำนวน lead ที่ค้างสถานะ new ต้นสัปดาห์
        'unit': 'ราย',
        'tracking': 'auto',
        'metric_key': 'lead_follow_up',
        'note': 'เป้ารายสัปดาห์ = จำนวน lead ที่ยังค้างสถานะ "new" ตอนต้นสัปดาห์ '
                '· ตัวจริง = จำนวนที่เปลี่ยนสถานะออกจาก new ในสัปดาห์นี้ (ประมาณจาก updated_at เพราะยังไม่มี '
                'LeadActivity log — ดู roadmap.py เฟส 9 กลุ่ม ค.) '
                '· ข้อเท็จจริง 27 ส.ค. 69: 18/19 lead ค้างสถานะ new เพราะไม่มีอะไรทวง',
    },
    {
        'key': 'testimonial',
        'name': 'ขอ testimonial จากร้าน Bergen (Muskelterapeut)',
        'icon': 'bi bi-chat-quote',
        'cadence': ONCE,
        'target': 1,
        'unit': 'ครั้ง',
        'tracking': 'manual',
        'manual_status': NOT_STARTED,
        'note': 'Sales ตรวจพบ 27 ส.ค. 69 — ใช้งานจริงมาหลายเดือนแล้วแต่ยังไม่เคยขอ = ของฟรีที่ทิ้งอยู่ '
                'ทำครั้งเดียวจบ ไม่ต้องรีเซ็ตทุกสัปดาห์ แก้ manual_status เป็น done_once เมื่อได้แล้ว',
    },
    {
        'key': 'expense_logging',
        'name': 'ลง Expense ทุกรายการที่เกิดขึ้น',
        'icon': 'bi bi-receipt',
        'cadence': WEEKLY,
        'target': None,  # ไม่มีเป้าตัวเลขตายตัว — วัดแค่ว่ามีการลงจริงต่อเนื่องไหม
        'unit': 'รายการ',
        'tracking': 'auto',
        'metric_key': 'expense_logging',
        'note': 'Marketing ตรวจพบ 27 ส.ค. 69 — Expense มี 0 แถว แปลว่าไม่รู้ต้นทุนตัวเอง คำนวณ CAC ไม่ได้ '
                'ทั้งที่เป็น KPI ที่ gtm_strategy.html ประกาศไว้เอง · นับจาก finance.Expense ที่บันทึกในสัปดาห์นี้',
    },
]


# ---------------------------------------------------------------------------
# ฟังก์ชันช่วยคำนวณ — หน้าเว็บเรียกใช้จากที่นี่ที่เดียว (คู่กับ dashboard/roadmap.py build_phases)
# ---------------------------------------------------------------------------
def week_range(today):
    """คืน (จันทร์, อาทิตย์) ของสัปดาห์ที่ today อยู่"""
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def previous_week_range(today):
    monday, _ = week_range(today)
    prev_monday = monday - timedelta(days=7)
    prev_sunday = monday - timedelta(days=1)
    return prev_monday, prev_sunday


def _trend(actual, prev):
    """เทียบสัปดาห์นี้กับสัปดาห์ก่อน คืน (ทิศทาง, ข้อความ) — ไม่ใช้ chart library"""
    if prev in (None, 0) and actual in (None, 0):
        return 'flat', 'ไม่มีข้อมูลเทียบ'
    if prev in (None, 0):
        return 'up', 'สัปดาห์ก่อนเป็น 0'
    diff = actual - prev
    pct = round(diff * 100 / prev)
    if diff > 0:
        return 'up', f'▲ +{pct}% เทียบสัปดาห์ก่อน'
    if diff < 0:
        return 'down', f'▼ {pct}% เทียบสัปดาห์ก่อน'
    return 'flat', '— เท่าเดิม'


def build_channels(metrics=None):
    """คืนรายการ channel พร้อมสถานะเทียบเป้า, % และแนวโน้ม

    metrics — dict ตัวเลขจริงจาก DB ที่ view คำนวณมาให้ (ดู dashboard.views.playbook_view)
               คีย์ที่ view ต้องส่งมา: <metric_key>, <metric_key>_prev, และสำหรับ target แบบ dynamic
               ต้องมี <metric_key>_target ด้วย (ตอนนี้มีแค่ lead_follow_up)
    """
    metrics = metrics or {}
    result = []
    for ch in CHANNELS:
        item = {**ch, 'meta': None, 'actual': None, 'target_resolved': ch.get('target'),
                 'pct': None, 'trend_dir': None, 'trend_text': None}

        if ch['tracking'] == 'auto':
            mk = ch['metric_key']
            actual = metrics.get(mk, 0)
            prev = metrics.get(f'{mk}_prev')
            target = metrics.get(f'{mk}_target', ch.get('target'))
            item['actual'] = actual
            item['target_resolved'] = target

            if target:
                pct = min(round(actual * 100 / target), 999)
                item['pct'] = pct
                item['status'] = ON_TARGET if actual >= target else (PARTIAL if actual > 0 else NOT_STARTED)
            else:
                item['status'] = TRACKED

            if prev is not None:
                item['trend_dir'], item['trend_text'] = _trend(actual, prev)

        else:  # manual
            status = ch.get('manual_status', NOT_STARTED)
            item['status'] = status
            item['actual'] = ch.get('target') if status == ON_TARGET else (
                ch.get('target') if status == DONE_ONCE else 0
            )

        item['meta'] = STATUS_META[item['status']]
        result.append(item)
    return result


def weekly_summary(metrics=None):
    """สรุปผลลัพธ์รวมของสัปดาห์ — ใช้แสดงการ์ดบนสุดของหน้า"""
    metrics = metrics or {}
    channels = build_channels(metrics)
    on_target = sum(1 for c in channels if c['status'] in (ON_TARGET, DONE_ONCE))
    not_started = sum(1 for c in channels if c['status'] == NOT_STARTED)
    total = len(channels)
    return {
        'total_channels': total,
        'on_target': on_target,
        'not_started': not_started,
        'leads_new': metrics.get('leads_new', 0),
        'leads_new_prev': metrics.get('leads_new_prev', 0),
        'leads_trend': _trend(metrics.get('leads_new', 0), metrics.get('leads_new_prev'))[1],
        'leads_trend_dir': _trend(metrics.get('leads_new', 0), metrics.get('leads_new_prev'))[0],
    }


# ---------------------------------------------------------------------------
# แผนนี้ถูกแก้ครั้งล่าสุดเมื่อไหร่ — เตือนถ้าไม่มีใครอัปเดต manual_status นานเกินไป
# กลไกเดียวกับ dashboard/roadmap.py แต่ไฟล์คนละไฟล์ จึงมีเวลาแก้ล่าสุดต่างกันได้
# ---------------------------------------------------------------------------
STALE_AFTER_DAYS = 10  # ยืดหยุ่นกว่า roadmap (7 วัน) เพราะบางสัปดาห์อาจไม่มีอะไรต้องแก้ในไฟล์ถ้าทุกอย่าง auto


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
