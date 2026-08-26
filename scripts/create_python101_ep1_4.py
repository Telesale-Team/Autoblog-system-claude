# -*- coding: utf-8 -*-
r"""
สร้างบทเรียน Python 101 EP1-EP4 (ช่วงที่ 1 — พื้นฐาน)

- อยู่ใน Category slug=python-101 (สร้างไว้แล้วตอน EP0)
- layout = "docs"  -> TOC อัตโนมัติ + callout/step/checklist + ซ่อน CTA ขายของ
- status = "draft" -> เจ้าของตรวจแล้วกด publish เอง
- insert HTML ตรงเข้า DB (ไม่ผ่าน CKEditor) -> inline SVG / callout ไม่โดน editor กิน
- <pre><code> จะได้ปุ่ม Copy อัตโนมัติจาก static/js/blog-code-copy.js

run: .\venv\Scripts\python.exe scripts\create_python101_ep1_4.py
"""
import os, sys, django

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_automate.settings")
django.setup()

from django.contrib.auth import get_user_model
from blog.models import Article, Category, Tag

User = get_user_model()

author = User.objects.filter(is_superuser=True).first() or User.objects.first()
category = Category.objects.get(slug="python-101")

# สไตล์ inline สำหรับกล่องเฉลย (docs mode ยังไม่มี CSS สำหรับ <details>)
DET = ('style="background:#0f1626;border:1px solid #1f2937;border-radius:10px;'
       'padding:0.9rem 1.1rem;margin:0.9rem 0;"')
SUM = 'style="cursor:pointer;color:#c9a96e;font-weight:700;font-size:0.92rem;"'

# ===================================================================
# ไดอะแกรม (inline SVG — attribute styling เท่านั้น กันคลาสรั่วทั้งหน้า)
# ===================================================================

SVG_HOW_PYTHON_RUNS = '''
<svg viewBox="0 0 760 210" role="img" aria-label="ไดอะแกรมแสดงว่าไฟล์ .py ถูก Python แปลเป็นผลลัพธ์บนหน้าจออย่างไร" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="45" width="200" height="120" rx="14" fill="#0f1626" stroke="#1f2937"/>
  <text x="40" y="74" font-family="Segoe UI,sans-serif" font-size="13" font-weight="700" fill="#f1f5f9">1. ไฟล์ที่เราเขียน</text>
  <text x="40" y="96" font-family="Consolas,monospace" font-size="12" fill="#94a3b8">hello.py</text>
  <rect x="40" y="108" width="160" height="40" rx="8" fill="#111827" stroke="#1f2937"/>
  <text x="52" y="133" font-family="Consolas,monospace" font-size="11.5" fill="#cbd5e1">print("สวัสดี")</text>
  <line x1="226" y1="105" x2="268" y2="105" stroke="#c9a96e" stroke-width="2"/>
  <polygon points="276,105 264,99 264,111" fill="#c9a96e"/>
  <rect x="282" y="45" width="196" height="120" rx="14" fill="#0f1626" stroke="#c9a96e" stroke-opacity="0.55"/>
  <text x="302" y="74" font-family="Segoe UI,sans-serif" font-size="13" font-weight="700" fill="#c9a96e">2. Python</text>
  <text x="302" y="96" font-family="Segoe UI,sans-serif" font-size="11.5" fill="#94a3b8">อ่านทีละบรรทัด</text>
  <text x="302" y="116" font-family="Segoe UI,sans-serif" font-size="11.5" fill="#94a3b8">บนลงล่าง</text>
  <text x="302" y="136" font-family="Segoe UI,sans-serif" font-size="11.5" fill="#94a3b8">แล้วทำตามทันที</text>
  <text x="302" y="156" font-family="Segoe UI,sans-serif" font-size="11" fill="#64748b">(นี่คือตัวที่เราจะติดตั้ง)</text>
  <line x1="484" y1="105" x2="526" y2="105" stroke="#c9a96e" stroke-width="2"/>
  <polygon points="534,105 522,99 522,111" fill="#c9a96e"/>
  <rect x="540" y="45" width="200" height="120" rx="14" fill="#0f1626" stroke="#10b981" stroke-opacity="0.5"/>
  <text x="560" y="74" font-family="Segoe UI,sans-serif" font-size="13" font-weight="700" fill="#4ade80">3. ผลลัพธ์บนจอ</text>
  <rect x="560" y="94" width="160" height="54" rx="8" fill="#020617" stroke="#1f2937"/>
  <text x="574" y="118" font-family="Consolas,monospace" font-size="11.5" fill="#4ade80">&gt; python hello.py</text>
  <text x="574" y="138" font-family="Consolas,monospace" font-size="12" fill="#e2e8f0">สวัสดี</text>
  <text x="20" y="192" font-family="Segoe UI,sans-serif" font-size="11.5" fill="#64748b">เราเขียนสูตร → Python อ่านสูตรแล้วทำตาม → เห็นผลทันที ไม่ต้องรอ compile</text>
</svg>'''

SVG_VARIABLE_BOX = '''
<svg viewBox="0 0 760 240" role="img" aria-label="ไดอะแกรมเปรียบตัวแปรเป็นกล่องติดป้ายชื่อ เก็บค่าไว้ข้างใน" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="28" font-family="Segoe UI,sans-serif" font-size="13.5" font-weight="700" fill="#f1f5f9">ตัวแปร = กล่องที่ติดป้ายชื่อไว้</text>
  <rect x="20" y="48" width="220" height="110" rx="12" fill="#0f1626" stroke="#c9a96e" stroke-opacity="0.45"/>
  <rect x="44" y="38" width="90" height="22" rx="6" fill="#111827" stroke="#c9a96e" stroke-opacity="0.6"/>
  <text x="89" y="53" text-anchor="middle" font-family="Consolas,monospace" font-size="11.5" fill="#c9a96e">price</text>
  <text x="130" y="112" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="26" font-weight="700" fill="#e2e8f0">250</text>
  <text x="130" y="138" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="11" fill="#64748b">ตัวเลขจำนวนเต็ม (int)</text>
  <rect x="270" y="48" width="220" height="110" rx="12" fill="#0f1626" stroke="#c9a96e" stroke-opacity="0.45"/>
  <rect x="294" y="38" width="90" height="22" rx="6" fill="#111827" stroke="#c9a96e" stroke-opacity="0.6"/>
  <text x="339" y="53" text-anchor="middle" font-family="Consolas,monospace" font-size="11.5" fill="#c9a96e">cost</text>
  <text x="380" y="112" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="26" font-weight="700" fill="#e2e8f0">180</text>
  <text x="380" y="138" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="11" fill="#64748b">ตัวเลขจำนวนเต็ม (int)</text>
  <rect x="520" y="48" width="220" height="110" rx="12" fill="#0f1626" stroke="#c9a96e" stroke-opacity="0.45"/>
  <rect x="544" y="38" width="110" height="22" rx="6" fill="#111827" stroke="#c9a96e" stroke-opacity="0.6"/>
  <text x="599" y="53" text-anchor="middle" font-family="Consolas,monospace" font-size="11.5" fill="#c9a96e">shop_name</text>
  <text x="630" y="110" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">"ร้านหนูดี"</text>
  <text x="630" y="138" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="11" fill="#64748b">ข้อความ (str) — มีเครื่องหมายคำพูด</text>
  <rect x="20" y="182" width="720" height="44" rx="10" fill="#111827" stroke="#1f2937"/>
  <text x="40" y="209" font-family="Consolas,monospace" font-size="12.5" fill="#cbd5e1">price = 250</text>
  <text x="180" y="209" font-family="Segoe UI,sans-serif" font-size="12" fill="#94a3b8">อ่านว่า "เอาค่า 250 ใส่ลงในกล่องชื่อ price" — ลูกศรพุ่งจากขวาไปซ้ายเสมอ</text>
</svg>'''

SVG_DATA_TYPES = '''
<svg viewBox="0 0 760 200" role="img" aria-label="ชนิดข้อมูล 4 แบบใน Python คือ str int float และ bool" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="26" font-family="Segoe UI,sans-serif" font-size="13.5" font-weight="700" fill="#f1f5f9">ชนิดข้อมูล 4 แบบที่ใช้จริง 95% ของงาน</text>
  <rect x="20" y="44" width="172" height="132" rx="12" fill="#0f1626" stroke="#1f2937"/>
  <text x="106" y="74" text-anchor="middle" font-family="Consolas,monospace" font-size="15" font-weight="700" fill="#c9a96e">str</text>
  <text x="106" y="96" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="12" fill="#cbd5e1">ข้อความ</text>
  <rect x="38" y="110" width="136" height="30" rx="7" fill="#111827"/>
  <text x="106" y="130" text-anchor="middle" font-family="Consolas,monospace" font-size="11.5" fill="#e2e8f0">"ร้านหนูดี"</text>
  <text x="106" y="160" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="10.5" fill="#64748b">ต้องมี " " ครอบเสมอ</text>
  <rect x="212" y="44" width="172" height="132" rx="12" fill="#0f1626" stroke="#1f2937"/>
  <text x="298" y="74" text-anchor="middle" font-family="Consolas,monospace" font-size="15" font-weight="700" fill="#c9a96e">int</text>
  <text x="298" y="96" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="12" fill="#cbd5e1">จำนวนเต็ม</text>
  <rect x="230" y="110" width="136" height="30" rx="7" fill="#111827"/>
  <text x="298" y="130" text-anchor="middle" font-family="Consolas,monospace" font-size="11.5" fill="#e2e8f0">250</text>
  <text x="298" y="160" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="10.5" fill="#64748b">ไม่มีจุดทศนิยม</text>
  <rect x="404" y="44" width="172" height="132" rx="12" fill="#0f1626" stroke="#1f2937"/>
  <text x="490" y="74" text-anchor="middle" font-family="Consolas,monospace" font-size="15" font-weight="700" fill="#c9a96e">float</text>
  <text x="490" y="96" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="12" fill="#cbd5e1">ทศนิยม</text>
  <rect x="422" y="110" width="136" height="30" rx="7" fill="#111827"/>
  <text x="490" y="130" text-anchor="middle" font-family="Consolas,monospace" font-size="11.5" fill="#e2e8f0">249.50</text>
  <text x="490" y="160" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="10.5" fill="#64748b">ใช้กับเงิน น้ำหนัก</text>
  <rect x="596" y="44" width="144" height="132" rx="12" fill="#0f1626" stroke="#1f2937"/>
  <text x="668" y="74" text-anchor="middle" font-family="Consolas,monospace" font-size="15" font-weight="700" fill="#c9a96e">bool</text>
  <text x="668" y="96" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="12" fill="#cbd5e1">จริง / เท็จ</text>
  <rect x="612" y="110" width="112" height="30" rx="7" fill="#111827"/>
  <text x="668" y="130" text-anchor="middle" font-family="Consolas,monospace" font-size="11.5" fill="#4ade80">True</text>
  <text x="668" y="160" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="10.5" fill="#64748b">ใช้ตอนตัดสินใจ</text>
</svg>'''

SVG_INPUT_FLOW = '''
<svg viewBox="0 0 760 250" role="img" aria-label="ขั้นตอนการทำงานของโปรแกรมออกใบเสร็จ ตั้งแต่รับค่าจนพิมพ์ผลลัพธ์" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="26" font-family="Segoe UI,sans-serif" font-size="13.5" font-weight="700" fill="#f1f5f9">เส้นทางของข้อมูล ตั้งแต่คนพิมพ์ จนออกมาเป็นใบเสร็จ</text>
  <rect x="20" y="48" width="150" height="76" rx="12" fill="#0f1626" stroke="#1f2937"/>
  <text x="95" y="74" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="12" font-weight="700" fill="#cbd5e1">1. รับค่า</text>
  <text x="95" y="96" text-anchor="middle" font-family="Consolas,monospace" font-size="11" fill="#c9a96e">input()</text>
  <text x="95" y="114" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="10" fill="#64748b">คนพิมพ์เข้ามา</text>
  <line x1="176" y1="86" x2="208" y2="86" stroke="#c9a96e" stroke-width="2"/><polygon points="216,86 204,80 204,92" fill="#c9a96e"/>
  <rect x="222" y="48" width="150" height="76" rx="12" fill="#0f1626" stroke="#f59e0b" stroke-opacity="0.55"/>
  <text x="297" y="74" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="12" font-weight="700" fill="#fbbf24">2. แปลงชนิด</text>
  <text x="297" y="96" text-anchor="middle" font-family="Consolas,monospace" font-size="11" fill="#c9a96e">int() / float()</text>
  <text x="297" y="114" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="10" fill="#fbbf24">ขั้นที่คนลืมบ่อยที่สุด</text>
  <line x1="378" y1="86" x2="410" y2="86" stroke="#c9a96e" stroke-width="2"/><polygon points="418,86 406,80 406,92" fill="#c9a96e"/>
  <rect x="424" y="48" width="150" height="76" rx="12" fill="#0f1626" stroke="#1f2937"/>
  <text x="499" y="74" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="12" font-weight="700" fill="#cbd5e1">3. คำนวณ</text>
  <text x="499" y="96" text-anchor="middle" font-family="Consolas,monospace" font-size="11" fill="#c9a96e">price * qty</text>
  <text x="499" y="114" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="10" fill="#64748b">ได้ยอดรวม</text>
  <line x1="580" y1="86" x2="612" y2="86" stroke="#c9a96e" stroke-width="2"/><polygon points="620,86 608,80 608,92" fill="#c9a96e"/>
  <rect x="620" y="48" width="120" height="76" rx="12" fill="#0f1626" stroke="#10b981" stroke-opacity="0.5"/>
  <text x="680" y="74" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="12" font-weight="700" fill="#4ade80">4. จัดรูป</text>
  <text x="680" y="96" text-anchor="middle" font-family="Consolas,monospace" font-size="11" fill="#c9a96e">f"..."</text>
  <text x="680" y="114" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="10" fill="#64748b">พิมพ์ใบเสร็จ</text>
  <rect x="222" y="152" width="352" height="72" rx="10" fill="rgba(245,158,11,0.07)" stroke="rgba(245,158,11,0.35)"/>
  <text x="242" y="177" font-family="Segoe UI,sans-serif" font-size="12" font-weight="700" fill="#fbbf24">ทำไมต้องมีขั้นที่ 2</text>
  <text x="242" y="197" font-family="Segoe UI,sans-serif" font-size="11.5" fill="#e7d9bd">input() คืนค่าเป็น "ข้อความ" เสมอ แม้คนจะพิมพ์ตัวเลข</text>
  <text x="242" y="215" font-family="Consolas,monospace" font-size="11" fill="#cbd5e1">"12" * 2  →  "1212"   ไม่ใช่  24</text>
</svg>'''

SVG_IF_FLOW = '''
<svg viewBox="0 0 760 330" role="img" aria-label="แผนผังการทำงานของ if elif else ที่ตรวจเงื่อนไขจากบนลงล่างและหยุดที่ข้อแรกที่เป็นจริง" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="26" font-family="Segoe UI,sans-serif" font-size="13.5" font-weight="700" fill="#f1f5f9">Python ไล่เงื่อนไขจากบนลงล่าง แล้วหยุดทันทีที่เจอข้อแรกที่เป็นจริง</text>
  <rect x="250" y="42" width="200" height="40" rx="10" fill="#111827" stroke="#1f2937"/>
  <text x="350" y="67" text-anchor="middle" font-family="Consolas,monospace" font-size="12" fill="#cbd5e1">total = 3000</text>
  <line x1="350" y1="82" x2="350" y2="100" stroke="#475569" stroke-width="2"/><polygon points="350,108 344,96 356,96" fill="#475569"/>
  <rect x="200" y="108" width="300" height="42" rx="10" fill="#0f1626" stroke="#1f2937"/>
  <text x="220" y="134" font-family="Consolas,monospace" font-size="12" fill="#cbd5e1">if total &gt;= 5000:</text>
  <text x="404" y="134" font-family="Segoe UI,sans-serif" font-size="11.5" fill="#f87171">เท็จ ✗</text>
  <text x="516" y="134" font-family="Segoe UI,sans-serif" font-size="11" fill="#64748b">3000 ไม่ถึง 5000 → ข้ามไปข้อถัดไป</text>
  <line x1="350" y1="150" x2="350" y2="164" stroke="#475569" stroke-width="2"/><polygon points="350,172 344,160 356,160" fill="#475569"/>
  <rect x="200" y="172" width="300" height="42" rx="10" fill="#0f1626" stroke="#10b981" stroke-opacity="0.6"/>
  <text x="220" y="198" font-family="Consolas,monospace" font-size="12" fill="#e2e8f0">elif total &gt;= 2000:</text>
  <text x="404" y="198" font-family="Segoe UI,sans-serif" font-size="11.5" fill="#4ade80">จริง ✓</text>
  <text x="516" y="198" font-family="Segoe UI,sans-serif" font-size="11" fill="#4ade80">ทำบรรทัดข้างใน แล้วจบเลย</text>
  <rect x="200" y="230" width="300" height="42" rx="10" fill="#0f1626" stroke="#1f2937" stroke-dasharray="5 4" opacity="0.45"/>
  <text x="220" y="256" font-family="Consolas,monospace" font-size="12" fill="#64748b">elif total &gt;= 1000:</text>
  <text x="516" y="256" font-family="Segoe UI,sans-serif" font-size="11" fill="#64748b">ไม่ถูกตรวจเลย</text>
  <rect x="200" y="280" width="300" height="42" rx="10" fill="#0f1626" stroke="#1f2937" stroke-dasharray="5 4" opacity="0.45"/>
  <text x="220" y="306" font-family="Consolas,monospace" font-size="12" fill="#64748b">else:</text>
  <text x="516" y="306" font-family="Segoe UI,sans-serif" font-size="11" fill="#64748b">ไม่ถูกตรวจเลย</text>
  <text x="20" y="256" font-family="Segoe UI,sans-serif" font-size="11" fill="#94a3b8">2 ข้อล่างนี้</text>
  <text x="20" y="274" font-family="Segoe UI,sans-serif" font-size="11" fill="#94a3b8">ถูกข้ามทั้งหมด</text>
</svg>'''

SVG_INDENT = '''
<svg viewBox="0 0 760 230" role="img" aria-label="เปรียบเทียบการเว้นวรรคหน้าบรรทัด ว่าบรรทัดไหนอยู่ในเงื่อนไขและบรรทัดไหนอยู่นอก" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="26" font-family="Segoe UI,sans-serif" font-size="13.5" font-weight="700" fill="#f1f5f9">การเว้นวรรคหน้าบรรทัด คือสิ่งที่บอกว่า "บรรทัดนี้อยู่ในเงื่อนไขหรือเปล่า"</text>
  <rect x="20" y="46" width="350" height="164" rx="12" fill="#0f1626" stroke="#10b981" stroke-opacity="0.5"/>
  <text x="40" y="72" font-family="Segoe UI,sans-serif" font-size="12" font-weight="700" fill="#4ade80">ถูกต้อง ✓</text>
  <text x="40" y="100" font-family="Consolas,monospace" font-size="12" fill="#cbd5e1">if total &gt;= 1000:</text>
  <rect x="56" y="108" width="290" height="30" rx="6" fill="rgba(74,222,128,0.08)" stroke="rgba(74,222,128,0.3)"/>
  <text x="72" y="128" font-family="Consolas,monospace" font-size="12" fill="#e2e8f0">discount = 0.05</text>
  <text x="40" y="164" font-family="Consolas,monospace" font-size="12" fill="#cbd5e1">print("จบแล้ว")</text>
  <text x="40" y="190" font-family="Segoe UI,sans-serif" font-size="10.5" fill="#94a3b8">บรรทัดที่ย่อหน้า = ทำเฉพาะตอนเงื่อนไขจริง</text>
  <text x="40" y="204" font-family="Segoe UI,sans-serif" font-size="10.5" fill="#94a3b8">บรรทัดที่ชิดซ้าย = ทำทุกครั้ง</text>
  <rect x="392" y="46" width="348" height="164" rx="12" fill="#0f1626" stroke="#ef4444" stroke-opacity="0.45"/>
  <text x="412" y="72" font-family="Segoe UI,sans-serif" font-size="12" font-weight="700" fill="#fca5a5">ผิด ✗</text>
  <text x="412" y="100" font-family="Consolas,monospace" font-size="12" fill="#cbd5e1">if total &gt;= 1000:</text>
  <rect x="412" y="108" width="308" height="30" rx="6" fill="rgba(239,68,68,0.08)" stroke="rgba(239,68,68,0.3)"/>
  <text x="424" y="128" font-family="Consolas,monospace" font-size="12" fill="#e2e8f0">discount = 0.05</text>
  <text x="412" y="164" font-family="Consolas,monospace" font-size="11.5" fill="#fca5a5">IndentationError: expected an</text>
  <text x="412" y="182" font-family="Consolas,monospace" font-size="11.5" fill="#fca5a5">indented block</text>
  <text x="412" y="204" font-family="Segoe UI,sans-serif" font-size="10.5" fill="#94a3b8">ลืมเว้น 4 ช่อง → Python ไม่รู้ว่าจะทำอะไรถ้าเงื่อนไขจริง</text>
</svg>'''


# ===================================================================
# EP1
# ===================================================================
EP1 = """
<p>ก่อนจะสอนอะไรทั้งนั้น ผมอยากให้คุณได้เห็นโค้ดของตัวเองรันบนหน้าจอก่อนครับ
เพราะโมเมนต์ที่คอมพิวเตอร์ทำตามคำสั่งที่คุณพิมพ์เองเป็นครั้งแรก มันเปลี่ยนความรู้สึกจาก
"เขียนโปรแกรมมันไกลตัว" เป็น "อ๋อ แค่นี้เองเหรอ" ได้ทันที</p>

<div class="callout c-tip">
  <span class="ico">🎯</span>
  <p><span class="ttl">จบ EP นี้คุณจะทำอะไรได้</span>
  ติดตั้ง Python และโปรแกรมเขียนโค้ดลงเครื่องตัวเองได้ ·
  สร้างไฟล์ <code>.py</code> เป็น ·
  เขียนและรันโค้ดบรรทัดแรกให้ขึ้นข้อความบนหน้าจอได้จริง<br>
  <b>ใช้เวลา:</b> อ่าน 12 นาที + ลงมือทำ 25 นาที · <b>ต้องผ่านมาก่อน:</b> ไม่มี นี่คือบทแรก</p>
</div>

<h2>Python คืออะไรกันแน่</h2>

<p>หลายคนสับสนระหว่างคำว่า "ภาษา Python" กับ "โปรแกรม Python" ผมอธิบายให้ชัดตรงนี้ทีเดียวเลยครับ</p>

<div class="analogy">
  <span class="emoji">🗣️</span>
  <p><b>Python คือภาษา</b> ที่เราใช้เขียนคำสั่ง ส่วนสิ่งที่เรากำลังจะติดตั้งลงเครื่องคือ
  <b>"ล่าม" ที่อ่านภาษานี้ออก</b> คุณเขียนคำสั่งเป็นภาษา Python ล่ามอ่านทีละบรรทัด
  แล้วสั่งคอมพิวเตอร์ทำตาม — ถ้าไม่มีล่าม ไฟล์ที่คุณเขียนก็เป็นแค่ไฟล์ข้อความธรรมดา</p>
</div>

<figure>
  __SVG_HOW_PYTHON_RUNS__
  <figcaption>Python อ่านโค้ดทีละบรรทัดจากบนลงล่าง แล้วทำตามทันที</figcaption>
</figure>

<p>จุดสำคัญที่ต้องจำคือ <b>Python ทำงานจากบนลงล่าง ทีละบรรทัด</b> ไม่ข้าม ไม่ย้อน
(จนกว่าเราจะสั่งให้มันย้อน ซึ่งจะเรียนใน EP5) ถ้าโค้ดคุณให้ผลไม่ตรงที่คิด
90% ของกรณีคือลำดับบรรทัดผิด ไม่ใช่ Python พัง</p>

<h2>ติดตั้ง Python ลงเครื่อง</h2>

<div class="step">
  <div class="step__n">1</div>
  <div class="step__body">
    <h3>เข้าเว็บทางการแล้วโหลด</h3>
    <p>เปิด <code>python.org/downloads</code> เว็บจะตรวจเครื่องคุณให้เองแล้วขึ้นปุ่มเหลืองใหญ่ว่า
    "Download Python 3.x.x" กดปุ่มนั้นได้เลย ไม่ต้องเลือกเวอร์ชันเอง</p>
  </div>
</div>

<div class="step">
  <div class="step__n">2</div>
  <div class="step__body">
    <h3>เปิดไฟล์ที่โหลดมา แล้วติ๊กช่องสำคัญก่อนกด Install</h3>
    <p>หน้าแรกของตัวติดตั้งจะมีช่องเล็กๆ ข้างล่างเขียนว่า <b>"Add python.exe to PATH"</b>
    <b>ต้องติ๊กช่องนี้ก่อนเสมอ</b> แล้วค่อยกด "Install Now" รอประมาณ 2-3 นาที</p>
  </div>
</div>

<div class="callout c-danger">
  <span class="ico">🚫</span>
  <p><span class="ttl">ช่อง Add to PATH คือจุดที่คนพลาดมากที่สุดใน EP นี้</span>
  ถ้าไม่ติ๊ก เครื่องจะติดตั้ง Python สำเร็จ แต่พอคุณพิมพ์คำสั่งเรียกใช้ เครื่องจะบอกว่าหาไม่เจอ
  แล้วคุณจะงงมากว่าติดตั้งไปแล้วทำไมไม่มี — ถ้าเผลอกด Install ไปแล้ว
  ให้เปิดไฟล์ติดตั้งอีกครั้ง เลือก Modify แล้วติ๊กใหม่ได้ครับ ไม่ต้องลบทิ้ง</p>
</div>

<div class="step">
  <div class="step__n">3</div>
  <div class="step__body">
    <h3>เช็คว่าติดตั้งสำเร็จจริง</h3>
    <p>เปิดโปรแกรม Terminal ขึ้นมา — Windows กดปุ่ม Start พิมพ์ว่า <code>powershell</code> แล้ว Enter
    ส่วน Mac กด Command+Space พิมพ์ <code>terminal</code> แล้ว Enter
    จะได้หน้าต่างดำๆ ที่พิมพ์คำสั่งได้ พิมพ์บรรทัดนี้ลงไป</p>
  </div>
</div>

<pre><code>python --version</code></pre>

<p>ถ้าขึ้นข้อความประมาณ <code>Python 3.13.1</code> (เลขท้ายไม่ต้องตรงกับผมก็ได้)
แปลว่าเรียบร้อยครับ ถ้าขึ้นว่าไม่รู้จักคำสั่ง ให้ย้อนกลับไปทำข้อ 2 ใหม่โดยติ๊ก Add to PATH</p>

<div class="callout c-note">
  <span class="ico">💡</span>
  <p><span class="ttl">Mac มี Python ติดมาอยู่แล้วนะ</span>
  แต่เป็นเวอร์ชันเก่าที่ระบบใช้เอง ให้ติดตั้งตัวใหม่จาก python.org ทับไปเลยครับ ไม่มีปัญหา
  และบน Mac บางเครื่องต้องพิมพ์ <code>python3 --version</code> แทน — ถ้า <code>python</code> เฉยๆ ไม่ได้ผล ให้เติม 3 ต่อท้ายทุกคำสั่งในคอร์สนี้</p>
</div>

<h2>ติดตั้งที่ทำงานของเรา — VS Code</h2>

<p>ทางเทคนิคคุณเขียน Python ใน Notepad ก็ได้ครับ แต่มันจะทรมานมาก
เราจะใช้ VS Code ซึ่งเป็นโปรแกรมเขียนโค้ดที่ฟรี เบา และคนใช้เยอะที่สุดในโลกตอนนี้
ข้อดีคือมันจะเตือนคุณตั้งแต่ยังพิมพ์ไม่จบบรรทัดว่าตรงไหนผิด</p>

<div class="step">
  <div class="step__n">1</div>
  <div class="step__body">
    <h3>โหลดและติดตั้ง</h3>
    <p>เข้า <code>code.visualstudio.com</code> กดปุ่ม Download ตัวใหญ่ ติดตั้งแบบกด Next รัวๆ ได้เลย ไม่มีอะไรต้องตั้งค่าพิเศษ</p>
  </div>
</div>

<div class="step">
  <div class="step__n">2</div>
  <div class="step__body">
    <h3>ติดตั้งส่วนเสริมภาษา Python</h3>
    <p>เปิด VS Code → มองแถบไอคอนด้านซ้ายสุด กดรูป <b>สี่เหลี่ยม 4 ชิ้น</b> (Extensions)
    → ช่องค้นหาพิมพ์ว่า <code>Python</code> → ตัวแรกที่ผู้พัฒนาเป็น Microsoft กด <b>Install</b></p>
  </div>
</div>

<div class="step">
  <div class="step__n">3</div>
  <div class="step__body">
    <h3>สร้างโฟลเดอร์เก็บงานของคอร์สนี้</h3>
    <p>สร้างโฟลเดอร์ใหม่ในเครื่อง ตั้งชื่อว่า <code>python-course</code> (ใช้ชื่อภาษาอังกฤษ ไม่เว้นวรรค)
    แล้วใน VS Code เลือกเมนู File → Open Folder → เลือกโฟลเดอร์นี้
    ต่อไปงานทุก EP เราจะเก็บไว้ที่นี่ที่เดียว</p>
  </div>
</div>

<h2>เขียนโค้ดบรรทัดแรก</h2>

<p>ถึงเวลาแล้วครับ ใน VS Code กด <b>New File</b> (ไอคอนหน้ากระดาษมีเครื่องหมายบวก
อยู่ตรงชื่อโฟลเดอร์ทางซ้าย) ตั้งชื่อไฟล์ว่า <code>hello.py</code> — ส่วนที่สำคัญคือ
<b>นามสกุล .py</b> ซึ่งเป็นสิ่งที่บอกทุกคนว่านี่คือไฟล์ภาษา Python</p>

<p>พิมพ์บรรทัดนี้ลงไป <b>พิมพ์เองนะครับ อย่าก๊อป</b> จะได้เห็นว่า VS Code ช่วยเราตรงไหนบ้าง</p>

<pre><code>print("สวัสดีครับ ผมเขียนโปรแกรมเป็นแล้ว")</code></pre>

<p>กด Ctrl+S (Mac กด Command+S) เพื่อเซฟ แล้วรันด้วยวิธีใดวิธีหนึ่งใน 2 วิธีนี้</p>

<p><b>วิธีที่ 1 (ง่ายสุด)</b> — กดปุ่ม <b>สามเหลี่ยม ▷</b> มุมขวาบนของ VS Code</p>

<p><b>วิธีที่ 2 (แบบที่มืออาชีพใช้)</b> — เปิด Terminal ใน VS Code ด้วยเมนู Terminal → New Terminal แล้วพิมพ์</p>

<pre><code>python hello.py</code></pre>

<p>ด้านล่างจอจะขึ้นข้อความว่า</p>

<pre><code>สวัสดีครับ ผมเขียนโปรแกรมเป็นแล้ว</code></pre>

<p>ยินดีด้วยครับ นั่นคือโปรแกรมตัวแรกของคุณ 🎉</p>

<h2>มาแกะกันว่าบรรทัดนั้นแปลว่าอะไร</h2>

<p>โค้ดบรรทัดเดียวนั้นมีของ 3 อย่างซ่อนอยู่ และทั้ง 3 อย่างนี้จะอยู่กับคุณไปตลอดคอร์ส</p>

<pre><code>print("สวัสดีครับ ผมเขียนโปรแกรมเป็นแล้ว")
 ^^^^^ ^                            ^
  |    |                            |
  |    +-- เครื่องหมายคำพูด ครอบข้อความ
  |
  +-- ชื่อคำสั่ง แปลว่า "แสดงออกมาให้เห็น"</code></pre>

<ol>
  <li><code>print</code> คือ <b>คำสั่ง</b> แปลตรงตัวว่า "พิมพ์ออกมาให้เห็นบนจอ" เป็นคำสั่งที่คุณจะใช้บ่อยที่สุดในชีวิตการเขียนโปรแกรม</li>
  <li><code>( )</code> วงเล็บ คือที่สำหรับใส่ "ของที่จะให้คำสั่งนี้ทำงานด้วย" ทุกคำสั่งใน Python จะมีวงเล็บต่อท้ายเสมอ</li>
  <li><code>" "</code> เครื่องหมายคำพูด บอกว่าข้างในนี้คือ <b>ข้อความ</b> ไม่ใช่คำสั่ง — ถ้าลืมใส่ Python จะพยายามอ่านมันเป็นคำสั่งแล้วพัง</li>
</ol>

<p>ลองเล่นต่ออีกนิดครับ เพิ่มอีก 2 บรรทัด แล้วรันใหม่</p>

<pre><code>print("สวัสดีครับ ผมเขียนโปรแกรมเป็นแล้ว")
print("วันนี้วันแรกของการเรียน Python")
print(2026)</code></pre>

<p>สังเกตบรรทัดสุดท้ายนะครับ — <code>2026</code> ไม่มีเครื่องหมายคำพูด เพราะมันคือ<b>ตัวเลข</b> ไม่ใช่ข้อความ
เรื่องความต่างระหว่างตัวเลขกับข้อความจะเป็นพระเอกของ EP2 ครับ</p>

<h2>กับดักที่คุณจะเจอ</h2>

<div class="callout c-warn">
  <span class="ico">⚠️</span>
  <p><span class="ttl">1. ใช้เครื่องหมายคำพูดภาษาไทย</span>
  ถ้าคุณเผลอเปลี่ยนแป้นเป็นภาษาไทยแล้วพิมพ์ฟันหนู มันจะได้อักขระคนละตัวกัน
  Python จะฟ้อง <code>SyntaxError</code> ทันที — เครื่องหมายคำพูดต้องพิมพ์ตอนแป้นเป็นภาษาอังกฤษเท่านั้น</p>
</div>

<div class="callout c-warn">
  <span class="ico">⚠️</span>
  <p><span class="ttl">2. ลืมปิดวงเล็บ</span>
  <code>print("สวัสดี"</code> จะได้ error ว่า <code>SyntaxError: unexpected EOF</code>
  แปลว่า "อ่านจนจบไฟล์แล้วยังไม่เจอวงเล็บปิดเลย" — VS Code ช่วยได้เยอะเพราะมันใส่วงเล็บปิดให้อัตโนมัติ</p>
</div>

<div class="callout c-warn">
  <span class="ico">⚠️</span>
  <p><span class="ttl">3. ตั้งชื่อไฟล์ว่า python.py</span>
  ห้ามเด็ดขาดครับ เพราะจะไปชนกับชื่อของตัว Python เอง แล้วเกิดอาการแปลกๆ ที่หาสาเหตุยากมาก
  ใช้ชื่ออื่นเถอะครับ เช่น <code>hello.py</code>, <code>test01.py</code></p>
</div>

<div class="callout c-warn">
  <span class="ico">⚠️</span>
  <p><span class="ttl">4. พิมพ์ Print แทน print</span>
  Python แยกตัวพิมพ์ใหญ่-เล็กครับ <code>Print</code> กับ <code>print</code> คือคนละตัวกัน
  และ Python รู้จักแค่ <code>print</code> ตัวเล็กทั้งหมด</p>
</div>

<h2>ลงมือทำ</h2>

<p>ทำในไฟล์ใหม่ชื่อ <code>ep1_practice.py</code> ครับ</p>

<p><b>ข้อ 1 (ง่าย)</b> — เขียนโปรแกรมที่พิมพ์ชื่อร้านหรือชื่อธุรกิจของคุณ ที่อยู่ และเบอร์โทร ออกมา 3 บรรทัด</p>

<details __DET__>
  <summary __SUM__>ดูเฉลยข้อ 1</summary>
  <pre><code>print("ร้านกาแฟหนูดี")
print("123 ถนนสุขุมวิท กรุงเทพฯ")
print("โทร 02-123-4567")</code></pre>
</details>

<p><b>ข้อ 2 (กลาง)</b> — ทำให้ผลลัพธ์มีเส้นคั่นสวยๆ แบบนี้ (ใบ้: <code>print("=" * 30)</code> จะพิมพ์เครื่องหมาย = ติดกัน 30 ตัว)</p>

<pre><code>==============================
       ร้านกาแฟหนูดี
==============================</code></pre>

<details __DET__>
  <summary __SUM__>ดูเฉลยข้อ 2</summary>
  <pre><code>print("=" * 30)
print("       ร้านกาแฟหนูดี")
print("=" * 30)</code></pre>
  <p style="margin-top:0.7rem;">เคล็ดลับ: การเว้นวรรคหน้าชื่อร้านในข้อความ ใช้เพื่อดันให้อยู่กลางๆ — ยังไม่ต้องทำให้เป๊ะครับ EP3 เราจะมีวิธีที่ดีกว่านี้</p>
</details>

<p><b>ข้อ 3 (ท้าทาย)</b> — ลองพิมพ์ <code>print("สวัสดี" + "ครับ")</code> กับ <code>print("สวัสดี", "ครับ")</code>
แล้วดูว่าผลลัพธ์ต่างกันตรงไหน อธิบายให้ตัวเองฟังได้ว่าทำไม</p>

<details __DET__>
  <summary __SUM__>ดูเฉลยข้อ 3</summary>
  <p>แบบ <code>+</code> ได้ <code>สวัสดีครับ</code> (ติดกัน) เพราะเครื่องหมายบวกคือการ "ต่อข้อความเข้าด้วยกันตรงๆ"</p>
  <p>แบบ <code>,</code> ได้ <code>สวัสดี ครับ</code> (มีเว้นวรรค) เพราะจุลภาคคือการบอก print ว่า
  "นี่คือของ 2 ชิ้นแยกกันนะ" แล้ว print จะใส่เว้นวรรคคั่นให้เองอัตโนมัติ</p>
</details>

<h2>เช็คว่าคุณผ่าน EP นี้จริง</h2>

<div class="checklist">
  <ul>
    <li>พิมพ์ <code>python --version</code> ใน Terminal แล้วเห็นเลขเวอร์ชันขึ้นมา</li>
    <li>เปิด VS Code แล้วเห็นโฟลเดอร์ <code>python-course</code> อยู่แถบซ้าย</li>
    <li>สร้างไฟล์ <code>.py</code> เอง เซฟเอง และรันเองได้ โดยไม่ต้องเปิดบทเรียนดู</li>
    <li>อธิบายได้ว่า <code>print</code> ทำอะไร และทำไมข้อความต้องมีเครื่องหมายคำพูดครอบ</li>
  </ul>
</div>

<p>ถ้ายังติ๊กไม่ครบ 4 ข้อ อย่าเพิ่งไป EP2 นะครับ ย้อนกลับมาทำให้ครบก่อน
เพราะทุก EP หลังจากนี้จะสมมติว่าคุณสร้างไฟล์และรันโค้ดเองเป็นแล้ว</p>

<h2>EP หน้าเจออะไร</h2>

<p>ตอนนี้โปรแกรมของเรายัง "พูด" ได้อย่างเดียว มันยังจำอะไรไม่ได้เลย
EP2 เราจะสอนให้มันจำค่าต่างๆ ไว้ในสิ่งที่เรียกว่า <b>ตัวแปร</b>
แล้วเอาไปคำนวณต่อได้ ปลายทางของ EP2 คือ<b>เครื่องคิดเลขที่คิดกำไรร้านคุณได้จริง</b> ครับ</p>
"""


# ===================================================================
# EP2
# ===================================================================
EP2 = """
<p>โปรแกรมใน EP1 ของเราพูดได้อย่างเดียว บอกให้พูดอะไรก็พูด แต่จำอะไรไม่ได้เลย
EP นี้เราจะให้มันมี "ความจำ" ครับ และพอมันจำได้ มันก็เริ่มคำนวณแทนเราได้ทันที</p>

<div class="callout c-tip">
  <span class="ico">🎯</span>
  <p><span class="ttl">จบ EP นี้คุณจะทำอะไรได้</span>
  สร้างตัวแปรเก็บค่าไว้ใช้ต่อได้ · แยกออกว่าข้อมูลแต่ละอย่างเป็นชนิดไหน ·
  <b>เขียนเครื่องคิดเลขคิดกำไรร้านตัวเองได้ 1 ตัว</b><br>
  <b>ใช้เวลา:</b> อ่าน 15 นาที + ลงมือทำ 25 นาที · <b>ต้องผ่านมาก่อน:</b> EP1</p>
</div>

<p><b>ทบทวน 30 วินาที</b> — EP1 เราติดตั้ง Python กับ VS Code แล้วเขียน <code>print()</code>
เพื่อแสดงข้อความบนจอ และรู้ว่าข้อความต้องมีเครื่องหมายคำพูดครอบ แต่ตัวเลขไม่ต้อง</p>

<h2>ตัวแปรคือกล่องที่ติดป้ายชื่อไว้</h2>

<div class="analogy">
  <span class="emoji">📦</span>
  <p>ลองนึกถึง<b>กล่องเก็บของที่คุณเขียนป้ายแปะไว้ข้างกล่อง</b> เวลาจะใช้ของ คุณไม่ต้องจำว่าของอยู่ตรงไหน
  แค่เรียกชื่อบนป้ายก็หยิบถูก — ตัวแปรก็แบบเดียวกันเป๊ะ คุณเก็บค่าไว้ในกล่อง ตั้งชื่อกล่อง
  แล้วเรียกใช้ด้วยชื่อนั้นได้ตลอดทั้งโปรแกรม</p>
</div>

<figure>
  __SVG_VARIABLE_BOX__
  <figcaption>เครื่องหมาย = ไม่ได้แปลว่า "เท่ากับ" แต่แปลว่า "เอาค่าฝั่งขวา ใส่ลงกล่องฝั่งซ้าย"</figcaption>
</figure>

<p>ลองสร้างไฟล์ใหม่ชื่อ <code>ep2.py</code> แล้วพิมพ์ตามนี้ครับ</p>

<pre><code>shop_name = "ร้านกาแฟหนูดี"
price = 250

print(shop_name)
print(price)</code></pre>

<p>ผลที่ได้</p>

<pre><code>ร้านกาแฟหนูดี
250</code></pre>

<p>สังเกตให้ดีนะครับ ตอนเราสั่ง <code>print(shop_name)</code> เราไม่ได้ใส่เครื่องหมายคำพูด
เพราะเราไม่ได้อยากให้มันพิมพ์คำว่า "shop_name" ออกมา แต่อยากให้มัน<b>เปิดกล่องชื่อ shop_name แล้วเอาของข้างในออกมาพิมพ์</b></p>

<pre><code>print(shop_name)     # ได้: ร้านกาแฟหนูดี   ← เปิดกล่องเอาของข้างใน
print("shop_name")   # ได้: shop_name       ← พิมพ์ตัวหนังสือตรงๆ</code></pre>

<div class="callout c-note">
  <span class="ico">💡</span>
  <p><span class="ttl">เครื่องหมาย # คืออะไร</span>
  ทุกอย่างที่อยู่หลัง <code>#</code> ในบรรทัดนั้น Python จะไม่สนใจเลย เราเรียกว่า <b>คอมเมนต์</b>
  มีไว้เขียนโน้ตบอกตัวเองในอนาคตว่าโค้ดตรงนี้ทำอะไร ใช้ให้ติดเป็นนิสัยตั้งแต่วันนี้เลยครับ
  คุณจะขอบคุณตัวเองในอีก 3 เดือน</p>
</div>

<h2>ชนิดข้อมูล 4 แบบที่ต้องรู้</h2>

<p>Python แยกข้อมูลออกเป็นชนิด และมันสำคัญมากเพราะ<b>ข้อมูลคนละชนิดทำอะไรกันไม่ได้</b>
เหมือนคุณเอาน้ำหนัก 5 กิโลกรัม มาบวกกับ 3 ชั่วโมง แล้วถามว่าได้เท่าไหร่ — มันตอบไม่ได้</p>

<figure>
  __SVG_DATA_TYPES__
  <figcaption>มีชนิดอื่นอีกเยอะ แต่ 4 ตัวนี้ครอบคลุมงานส่วนใหญ่ที่คุณจะเจอ</figcaption>
</figure>

<p>ถ้าไม่แน่ใจว่าอะไรเป็นชนิดไหน ถาม Python ตรงๆ ได้ด้วยคำสั่ง <code>type()</code></p>

<pre><code>print(type("ร้านกาแฟหนูดี"))   # &lt;class 'str'&gt;
print(type(250))                # &lt;class 'int'&gt;
print(type(249.50))             # &lt;class 'float'&gt;
print(type(True))               # &lt;class 'bool'&gt;</code></pre>

<p>คำว่า <code>class</code> ยังไม่ต้องสนใจครับ ดูแค่คำหลัง <code>'</code> ก็พอ</p>

<h2>คำนวณด้วยตัวแปร</h2>

<p>พอค่าอยู่ในกล่องแล้ว เราเอากล่องมาบวกลบคูณหารกันได้เลย ตัวดำเนินการพื้นฐานมี 5 ตัว</p>

<pre><code>a = 10
b = 3

print(a + b)    # 13    บวก
print(a - b)    # 7     ลบ
print(a * b)    # 30    คูณ  (ใช้ดอกจัน ไม่ใช่ x)
print(a / b)    # 3.333 หาร  (ได้ทศนิยมเสมอ)
print(a % b)    # 1     เศษจากการหาร</code></pre>

<p>ที่ต้องระวังคือ <b>เครื่องหมายคูณคือ <code>*</code> ไม่ใช่ <code>x</code></b> เพราะ x ถูกใช้เป็นชื่อตัวแปรได้
ถ้าเขียน <code>a x b</code> Python จะงงทันที</p>

<h2>สร้างเครื่องคิดเลขคิดกำไรร้าน</h2>

<p>ถึงเวลาเอาของจริงมาใช้แล้วครับ สมมติว่าคุณขายกาแฟแก้วละ 250 บาท ต้นทุนแก้วละ 180 บาท
วันนี้ขายได้ 12 แก้ว — เราจะให้คอมพิวเตอร์คำนวณให้</p>

<pre><code># ==== ข้อมูลของร้าน (แก้ตัวเลขตรงนี้ให้เป็นของร้านคุณ) ====
shop_name = "ร้านกาแฟหนูดี"
price = 250        # ราคาขายต่อแก้ว
cost = 180         # ต้นทุนต่อแก้ว
qty = 12           # จำนวนที่ขายได้วันนี้

# ==== คำนวณ ====
revenue = price * qty            # ยอดขาย
total_cost = cost * qty          # ต้นทุนรวม
profit = revenue - total_cost    # กำไร

# ==== แสดงผล ====
print("สรุปยอดวันนี้ของ", shop_name)
print("ขายได้", qty, "แก้ว")
print("ยอดขาย", revenue, "บาท")
print("ต้นทุน", total_cost, "บาท")
print("กำไร", profit, "บาท")</code></pre>

<p>รันแล้วจะได้</p>

<pre><code>สรุปยอดวันนี้ของ ร้านกาแฟหนูดี
ขายได้ 12 แก้ว
ยอดขาย 3000 บาท
ต้นทุน 2160 บาท
กำไร 840 บาท</code></pre>

<p>ลองเปลี่ยนเลข <code>qty</code> จาก 12 เป็น 50 แล้วรันใหม่ครับ —
ตัวเลขทุกบรรทัดเปลี่ยนตามให้เองหมด <b>นี่คือพลังของตัวแปร</b>
คุณแก้ที่เดียว ที่เหลือมันคิดต่อให้เอง ถ้าเราไม่ใช้ตัวแปร คุณต้องนั่งแก้ตัวเลขทุกบรรทัดเอง</p>

<div class="callout c-tip">
  <span class="ico">💰</span>
  <p><span class="ttl">ลองต่อยอดเลย</span>
  เพิ่มบรรทัด <code>margin = profit / revenue * 100</code> แล้ว print ออกมา
  คุณจะได้ % กำไรของร้านทันที ซึ่งเป็นตัวเลขที่เจ้าของร้านควรรู้แต่ส่วนใหญ่ไม่เคยคำนวณ</p>
</div>

<h2>กับดักที่คุณจะเจอ</h2>

<div class="callout c-danger">
  <span class="ico">🚫</span>
  <p><span class="ttl">1. เอาข้อความไปบวกกับตัวเลข</span>
  <code>"250" + 50</code> จะพังทันทีด้วย <code>TypeError</code>
  เพราะ <code>"250"</code> ที่มีคำพูดครอบคือ<b>ข้อความ</b> ไม่ใช่ตัวเลข
  ถ้าอยากแปลงให้ใช้ <code>int("250") + 50</code> จะได้ 300 —
  เรื่องนี้จะกลับมาหลอกหลอนคุณอีกครั้งใน EP3 ครับ จำไว้ให้ดี</p>
</div>

<div class="callout c-warn">
  <span class="ico">⚠️</span>
  <p><span class="ttl">2. ตั้งชื่อตัวแปรผิดกติกา</span>
  ห้ามขึ้นต้นด้วยตัวเลข (<code>2price</code> ไม่ได้) ห้ามมีเว้นวรรค (<code>shop name</code> ไม่ได้ ใช้ <code>shop_name</code>)
  และห้ามใช้คำสงวนของ Python เช่น <code>print</code>, <code>if</code>, <code>list</code> เป็นชื่อตัวแปร</p>
</div>

<div class="callout c-warn">
  <span class="ico">⚠️</span>
  <p><span class="ttl">3. ใช้ตัวแปรก่อนสร้าง</span>
  Python อ่านจากบนลงล่าง ถ้าคุณ <code>print(profit)</code> ก่อนบรรทัดที่คำนวณ <code>profit</code>
  จะเจอ <code>NameError: name 'profit' is not defined</code> แปลว่า "ไม่รู้จักกล่องชื่อนี้" —
  ต้องสร้างกล่องก่อนเสมอ แล้วค่อยเรียกใช้</p>
</div>

<div class="callout c-note">
  <span class="ico">💡</span>
  <p><span class="ttl">ทำไมไม่ตั้งชื่อตัวแปรเป็นภาษาไทย</span>
  ทางเทคนิคทำได้ครับ <code>ราคา = 250</code> Python ยอมรับ แต่ผมไม่แนะนำ
  เพราะเวลาไปดูโค้ดคนอื่น ค้นหาวิธีแก้ปัญหาใน Google หรือให้ AI ช่วยเขียน
  ทุกอย่างเป็นภาษาอังกฤษหมด การชินกับชื่ออังกฤษตั้งแต่วันแรกจะช่วยคุณมากในระยะยาว
  ส่วน<b>คอมเมนต์เขียนไทยได้เต็มที่</b>ครับ</p>
</div>

<h2>ลงมือทำ</h2>

<p><b>ข้อ 1 (ง่าย)</b> — สร้างตัวแปร 3 ตัวเก็บชื่อคุณ อายุ และส่วนสูง แล้ว print ออกมาทั้งหมด
พร้อมเช็คด้วย <code>type()</code> ว่าแต่ละตัวเป็นชนิดอะไร</p>

<details __DET__>
  <summary __SUM__>ดูเฉลยข้อ 1</summary>
  <pre><code>name = "ภูมิพัฒน์"
age = 35
height = 172.5

print(name, age, height)
print(type(name))     # str
print(type(age))      # int
print(type(height))   # float</code></pre>
</details>

<p><b>ข้อ 2 (กลาง)</b> — แก้เครื่องคิดเลขข้างบนให้คำนวณ<b>เปอร์เซ็นต์กำไร</b>เพิ่ม
และให้แสดงผลว่า "กำไร 840 บาท (28.0%)"</p>

<details __DET__>
  <summary __SUM__>ดูเฉลยข้อ 2</summary>
  <pre><code>price = 250
cost = 180
qty = 12

revenue = price * qty
profit = (price - cost) * qty
margin = profit / revenue * 100

print("กำไร", profit, "บาท", "(", margin, "%)")</code></pre>
  <p style="margin-top:0.7rem;">จะเห็นว่าผลออกมาหน้าตายังไม่สวย มีเว้นวรรคเกินรอบวงเล็บ
  และทศนิยมยาวเกินจำเป็น — EP3 เราจะได้เครื่องมือจัดข้อความให้สวยกว่านี้ครับ</p>
</details>

<p><b>ข้อ 3 (ท้าทาย)</b> — ร้านคุณมีสินค้า 2 อย่าง กาแฟ (ขาย 250 ทุน 180 ขายได้ 12)
และเค้ก (ขาย 120 ทุน 70 ขายได้ 25) เขียนโปรแกรมสรุปกำไรรวมของทั้งร้าน
และบอกด้วยว่าสินค้าไหนทำกำไรได้มากกว่า</p>

<details __DET__>
  <summary __SUM__>ดูเฉลยข้อ 3</summary>
  <pre><code>coffee_profit = (250 - 180) * 12    # 840
cake_profit = (120 - 70) * 25       # 1250
total = coffee_profit + cake_profit

print("กำไรกาแฟ", coffee_profit, "บาท")
print("กำไรเค้ก", cake_profit, "บาท")
print("กำไรรวม", total, "บาท")</code></pre>
  <p style="margin-top:0.7rem;">เค้กทำกำไรมากกว่า (1,250 บาท) ทั้งที่ราคาถูกกว่าครึ่ง —
  ส่วนการให้โปรแกรม<b>ตอบเองว่าตัวไหนมากกว่า</b> ต้องใช้เงื่อนไข ซึ่งเป็นเรื่องของ EP4 ครับ</p>
</details>

<h2>เช็คว่าคุณผ่าน EP นี้จริง</h2>

<div class="checklist">
  <ul>
    <li>อธิบายได้ว่า <code>price = 250</code> ทำงานยังไง และทำไม = ไม่ได้แปลว่า "เท่ากับ"</li>
    <li>บอกความต่างระหว่าง <code>250</code> กับ <code>"250"</code> ได้</li>
    <li>เครื่องคิดเลขกำไรของคุณรันได้ และเปลี่ยนตัวเลขแล้วผลลัพธ์เปลี่ยนตามถูกต้อง</li>
    <li>เขียนคอมเมนต์ด้วย <code>#</code> อธิบายโค้ดตัวเองได้</li>
  </ul>
</div>

<h2>EP หน้าเจออะไร</h2>

<p>ตอนนี้โปรแกรมของเรายังต้องให้คุณเข้าไปแก้ตัวเลขในโค้ดเองทุกครั้ง ซึ่งคนอื่นใช้ไม่ได้เลย
EP3 เราจะทำให้โปรแกรม<b>ถามผู้ใช้เอง</b>ว่าขายอะไร กี่ชิ้น แล้วออกใบเสร็จหน้าตาสวยๆ ให้
พร้อมเรียนวิธีจัดข้อความให้ตัวเลขมีลูกน้ำคั่นหลักพันและทศนิยม 2 ตำแหน่งเป๊ะครับ</p>
"""


# ===================================================================
# EP3
# ===================================================================
EP3 = """
<p>โปรแกรมของเราตอนนี้เก่งขึ้นเยอะ คิดกำไรได้แล้ว แต่ยังมีปัญหาใหญ่อยู่ข้อหนึ่ง —
ทุกครั้งที่อยากเปลี่ยนตัวเลข คุณต้องเปิดโค้ดเข้าไปแก้เอง
ซึ่งแปลว่าคนอื่นที่ไม่ใช่คุณ ใช้โปรแกรมนี้ไม่ได้เลย EP นี้เราจะแก้เรื่องนั้นครับ</p>

<div class="callout c-tip">
  <span class="ico">🎯</span>
  <p><span class="ttl">จบ EP นี้คุณจะทำอะไรได้</span>
  ทำให้โปรแกรมถามข้อมูลจากผู้ใช้เองได้ · แปลงข้อความเป็นตัวเลขเป็น ·
  จัดรูปแบบตัวเลขให้มีลูกน้ำและทศนิยมสวยงาม · <b>เขียนโปรแกรมออกใบเสร็จได้ 1 ตัว</b><br>
  <b>ใช้เวลา:</b> อ่าน 15 นาที + ลงมือทำ 30 นาที · <b>ต้องผ่านมาก่อน:</b> EP1, EP2</p>
</div>

<p><b>ทบทวน 30 วินาที</b> — EP2 เราเก็บค่าไว้ในตัวแปร รู้จักชนิดข้อมูล 4 แบบ (str, int, float, bool)
และเจอกับดักสำคัญว่า <code>"250"</code> ที่มีคำพูดครอบ คือข้อความ เอาไปคำนวณตรงๆ ไม่ได้ — จำไว้ให้ดี เพราะมันจะกลับมาใน EP นี้</p>

<h2>input — ให้โปรแกรมถามเราเป็น</h2>

<p>คำสั่งเดียวที่ต้องรู้คือ <code>input()</code> ครับ มันจะหยุดโปรแกรมไว้ รอให้คนพิมพ์ แล้วกด Enter</p>

<pre><code>name = input("คุณชื่ออะไร: ")
print("สวัสดีครับคุณ", name)</code></pre>

<p>รันแล้วโปรแกรมจะหยุดรอ พอคุณพิมพ์ชื่อแล้วกด Enter จะได้</p>

<pre><code>คุณชื่ออะไร: ภูมิพัฒน์
สวัสดีครับคุณ ภูมิพัฒน์</code></pre>

<p>ข้อความในวงเล็บของ <code>input()</code> คือ<b>คำถามที่จะขึ้นบนจอ</b>
ควรใส่เสมอและใส่ให้ชัดว่าต้องการอะไร ไม่งั้นคนใช้จะงงว่าโปรแกรมค้างหรือรออะไรอยู่</p>

<h2>กับดักที่ทำให้มือใหม่ติดกันทุกคน</h2>

<p>ลองรันโค้ดนี้ครับ แล้วเดาก่อนว่าจะได้อะไร</p>

<pre><code>qty = input("ซื้อกี่ชิ้น: ")
print(qty * 2)</code></pre>

<p>ถ้าคุณพิมพ์ <code>12</code> คุณอาจคิดว่าจะได้ 24 แต่ผลจริงคือ</p>

<pre><code>1212</code></pre>

<div class="callout c-danger">
  <span class="ico">🚫</span>
  <p><span class="ttl">input() คืนค่าเป็นข้อความเสมอ ไม่ว่าคุณจะพิมพ์อะไรลงไป</span>
  แม้พิมพ์ตัวเลขล้วน Python ก็มองว่าเป็นข้อความ <code>"12"</code> อยู่ดี
  พอเอาไปคูณ 2 มันเลยแปลว่า "ต่อข้อความนี้ซ้ำ 2 รอบ" ได้ <code>"1212"</code>
  <b>นี่คือบั๊กอันดับ 1 ของคนเริ่มต้น</b> และตอนนี้คุณรู้ทันแล้ว</p>
</div>

<p>วิธีแก้คือครอบด้วย <code>int()</code> สำหรับจำนวนเต็ม หรือ <code>float()</code> สำหรับทศนิยม</p>

<pre><code>qty = int(input("ซื้อกี่ชิ้น: "))       # แปลงเป็นจำนวนเต็ม
price = float(input("ราคาต่อชิ้น: "))   # แปลงเป็นทศนิยม (ใช้กับเงิน)

print(qty * 2)      # คราวนี้ได้ 24 แล้ว</code></pre>

<p>อ่านจากในออกนอกนะครับ — <code>input()</code> ทำงานก่อนได้ข้อความมา
แล้ว <code>int()</code> ที่ครอบอยู่ข้างนอกค่อยแปลงเป็นตัวเลข</p>

<figure>
  __SVG_INPUT_FLOW__
  <figcaption>จำลำดับนี้ให้ขึ้นใจ — ขั้นที่ 2 คือขั้นที่คนลืมบ่อยที่สุด</figcaption>
</figure>

<div class="callout c-note">
  <span class="ico">💡</span>
  <p><span class="ttl">เมื่อไหร่ใช้ int เมื่อไหร่ใช้ float</span>
  ของที่นับเป็นชิ้นได้ ไม่มีทางเป็นเศษ → <code>int</code> เช่น จำนวนสินค้า จำนวนคน<br>
  ของที่มีเศษได้ → <code>float</code> เช่น ราคา น้ำหนัก ส่วนสูง<br>
  ถ้าไม่แน่ใจ ใช้ <code>float</code> ไว้ก่อนปลอดภัยกว่าครับ</p>
</div>

<h2>f-string — จัดข้อความให้ออกมาสวย</h2>

<p>ใน EP2 เราพิมพ์ผลลัพธ์ด้วยการใส่จุลภาคคั่นไปเรื่อยๆ ซึ่งได้ผลแต่หน้าตาไม่สวย
และคุมเว้นวรรคไม่ได้ Python มีวิธีที่ดีกว่ามากชื่อว่า <b>f-string</b></p>

<p>วิธีใช้คือ<b>เติมตัว f ไว้หน้าเครื่องหมายคำพูด</b> แล้วเอาชื่อตัวแปรใส่ในปีกกา</p>

<pre><code>name = "ภูมิพัฒน์"
total = 3000

# แบบเก่าจาก EP2
print("คุณ", name, "ยอดรวม", total, "บาท")

# แบบ f-string — อ่านง่ายกว่า คุมเว้นวรรคได้เป๊ะ
print(f"คุณ {name} ยอดรวม {total} บาท")</code></pre>

<p>ทั้งสองแบบให้ผลใกล้เคียงกัน แต่แบบ f-string คุณเห็นหน้าตาผลลัพธ์ได้เลยตั้งแต่ตอนเขียน
และในปีกกาใส่การคำนวณลงไปตรงๆ ได้ด้วย</p>

<pre><code>price = 250
qty = 12
print(f"ยอดรวม {price * qty} บาท")     # ยอดรวม 3000 บาท</code></pre>

<h3>จัดรูปแบบตัวเลขให้เป็นมืออาชีพ</h3>

<p>ความสามารถที่ทำให้ f-string เหนือกว่าคือการ<b>จัดรูปแบบตัวเลข</b> ด้วยการเติมโค้ดสั้นๆ หลังเครื่องหมาย <code>:</code></p>

<pre><code>total = 1234567.891

print(f"{total}")           # 1234567.891      ดิบๆ อ่านยาก
print(f"{total:.2f}")       # 1234567.89       ทศนิยม 2 ตำแหน่ง
print(f"{total:,.2f}")      # 1,234,567.89     มีลูกน้ำคั่นหลักพัน
print(f"{total:,.0f}")      # 1,234,568        ปัดเป็นจำนวนเต็ม</code></pre>

<p>จำแค่ <code>:,.2f</code> ตัวเดียวก็พอครับ แปลว่า "ใส่ลูกน้ำคั่นหลักพัน และเอาทศนิยม 2 ตำแหน่ง"
ซึ่งเป็นรูปแบบมาตรฐานของการแสดงเงินทั่วโลก</p>

<h2>สร้างโปรแกรมออกใบเสร็จ</h2>

<p>เอาทุกอย่างมารวมกันครับ สร้างไฟล์ <code>ep3_receipt.py</code></p>

<pre><code># ==== รับข้อมูลจากผู้ใช้ ====
shop = "ร้านกาแฟหนูดี"
customer = input("ชื่อลูกค้า: ")
item = input("สินค้า: ")
price = float(input("ราคาต่อชิ้น: "))
qty = int(input("จำนวน: "))

# ==== คำนวณ ====
subtotal = price * qty
vat = subtotal * 0.07
total = subtotal + vat

# ==== พิมพ์ใบเสร็จ ====
print()
print("=" * 34)
print(f"{shop:^34}")
print("=" * 34)
print(f"ลูกค้า  : {customer}")
print(f"สินค้า  : {item}")
print(f"ราคา    : {price:,.2f} x {qty}")
print("-" * 34)
print(f"ยอดรวม  : {subtotal:>13,.2f} บาท")
print(f"VAT 7%  : {vat:>13,.2f} บาท")
print(f"สุทธิ    : {total:>13,.2f} บาท")
print("=" * 34)
print("ขอบคุณที่ใช้บริการครับ")</code></pre>

<p>รันแล้วลองใส่ข้อมูลดู จะได้ประมาณนี้</p>

<pre><code>ชื่อลูกค้า: คุณสมชาย
สินค้า: ลาเต้เย็น
ราคาต่อชิ้น: 85
จำนวน: 3

==================================
          ร้านกาแฟหนูดี
==================================
ลูกค้า  : คุณสมชาย
สินค้า  : ลาเต้เย็น
ราคา    : 85.00 x 3
----------------------------------
ยอดรวม  :        255.00 บาท
VAT 7%  :         17.85 บาท
สุทธิ    :        272.85 บาท
==================================
ขอบคุณที่ใช้บริการครับ</code></pre>

<p>มีของใหม่ 2 อย่างในโค้ดนี้ที่ผมยังไม่ได้อธิบายครับ</p>

<ul>
  <li><code>{shop:^34}</code> — เครื่องหมาย <b>^</b> แปลว่า "จัดกึ่งกลางในพื้นที่กว้าง 34 ช่อง"</li>
  <li><code>{subtotal:>13,.2f}</code> — เครื่องหมาย <b>&gt;</b> แปลว่า "ชิดขวาในพื้นที่กว้าง 13 ช่อง"
  ซึ่งทำให้ตัวเลขทุกบรรทัดเรียงหลักตรงกันสวยงาม</li>
</ul>

<p>ยังมี <code>&lt;</code> สำหรับชิดซ้ายอีกตัว ทั้ง 3 ตัวนี้คือเครื่องมือจัดตารางแบบง่ายๆ ที่ใช้ได้ยาวๆ ครับ</p>

<div class="callout c-tip">
  <span class="ico">✨</span>
  <p><span class="ttl">print() เปล่าๆ ทำอะไร</span>
  บรรทัด <code>print()</code> ที่ไม่มีอะไรในวงเล็บ คือการเว้นบรรทัดว่าง 1 บรรทัด
  ใช้เยอะมากเวลาอยากให้ผลลัพธ์อ่านง่ายขึ้นครับ</p>
</div>

<h2>กับดักที่คุณจะเจอ</h2>

<div class="callout c-danger">
  <span class="ico">🚫</span>
  <p><span class="ttl">1. ลืมครอบด้วย int() หรือ float()</span>
  อาการคือตัวเลขซ้ำกันแปลกๆ (<code>1212</code>) หรือพังด้วย
  <code>TypeError: can't multiply sequence by non-int</code>
  วิธีเช็คเร็วที่สุดคือ <code>print(type(qty))</code> ถ้าขึ้น <code>str</code> แปลว่าลืมแปลง</p>
</div>

<div class="callout c-warn">
  <span class="ico">⚠️</span>
  <p><span class="ttl">2. ผู้ใช้พิมพ์ตัวหนังสือตอนที่โปรแกรมขอตัวเลข</span>
  ถ้าโปรแกรมถามจำนวนแล้วคนพิมพ์ว่า "สามชิ้น" จะพังด้วย <code>ValueError: invalid literal for int()</code>
  ตอนนี้ยังแก้ไม่ได้ครับ ต้องรอ EP9 ที่เราจะเรียนวิธีดักข้อผิดพลาด —
  ระหว่างนี้ก็พิมพ์ตัวเลขให้ถูกไปก่อนนะครับ</p>
</div>

<div class="callout c-warn">
  <span class="ico">⚠️</span>
  <p><span class="ttl">3. ลืมใส่ f หน้าเครื่องหมายคำพูด</span>
  <code>print("ยอดรวม {total} บาท")</code> จะพิมพ์ปีกกาออกมาตรงๆ เป็น
  <code>ยอดรวม {total} บาท</code> ซึ่งไม่ error แต่ผลลัพธ์ผิด
  ข้อนี้อันตรายกว่า error เพราะโปรแกรมไม่เตือนคุณเลย ต้องตาไวเอง</p>
</div>

<h2>ลงมือทำ</h2>

<p><b>ข้อ 1 (ง่าย)</b> — เขียนโปรแกรมถามชื่อกับปีเกิด แล้วบอกอายุออกมา (ใช้ 2569 ลบปีเกิด)</p>

<details __DET__>
  <summary __SUM__>ดูเฉลยข้อ 1</summary>
  <pre><code>name = input("ชื่อ: ")
birth_year = int(input("ปีเกิด (พ.ศ.): "))
age = 2569 - birth_year

print(f"สวัสดีครับคุณ {name} ปีนี้อายุ {age} ปี")</code></pre>
</details>

<p><b>ข้อ 2 (กลาง)</b> — แก้โปรแกรมใบเสร็จให้รับสินค้าได้ <b>2 รายการ</b> แล้วรวมยอดทั้งหมด</p>

<details __DET__>
  <summary __SUM__>ดูเฉลยข้อ 2</summary>
  <pre><code>item1 = input("สินค้าชิ้นที่ 1: ")
price1 = float(input("ราคา: "))
qty1 = int(input("จำนวน: "))

item2 = input("สินค้าชิ้นที่ 2: ")
price2 = float(input("ราคา: "))
qty2 = int(input("จำนวน: "))

sub1 = price1 * qty1
sub2 = price2 * qty2
total = sub1 + sub2

print("-" * 34)
print(f"{item1:&lt;16}{sub1:>14,.2f}")
print(f"{item2:&lt;16}{sub2:>14,.2f}")
print("-" * 34)
print(f"{'รวมทั้งสิ้น':&lt;16}{total:>14,.2f}")</code></pre>
  <p style="margin-top:0.7rem;">สังเกตว่าโค้ดเริ่มซ้ำซากแล้วใช่ไหมครับ ถ้ามี 20 รายการคงเขียนไม่ไหว —
  EP5 (ลิสต์กับลูป) จะแก้ปัญหานี้ให้เหลือไม่กี่บรรทัด</p>
</details>

<p><b>ข้อ 3 (ท้าทาย)</b> — เขียนโปรแกรมคำนวณเงินทอน ถามยอดที่ต้องจ่ายกับเงินที่ลูกค้าให้มา
แล้วบอกว่าต้องทอนเท่าไหร่ จัดรูปแบบให้มีลูกน้ำและทศนิยม 2 ตำแหน่ง</p>

<details __DET__>
  <summary __SUM__>ดูเฉลยข้อ 3</summary>
  <pre><code>total = float(input("ยอดที่ต้องจ่าย: "))
paid = float(input("ลูกค้าให้มา: "))
change = paid - total

print()
print(f"ยอดที่ต้องจ่าย : {total:>12,.2f} บาท")
print(f"รับมา          : {paid:>12,.2f} บาท")
print(f"เงินทอน        : {change:>12,.2f} บาท")</code></pre>
  <p style="margin-top:0.7rem;">ถ้าลูกค้าให้เงินไม่พอ ตัวเลขจะติดลบ ซึ่งโปรแกรมยังไม่รู้จักเตือน —
  EP4 เราจะสอนให้มันตรวจและเตือนเองครับ</p>
</details>

<h2>เช็คว่าคุณผ่าน EP นี้จริง</h2>

<div class="checklist">
  <ul>
    <li>อธิบายได้ว่าทำไม <code>input()</code> ต้องครอบด้วย <code>int()</code> หรือ <code>float()</code></li>
    <li>เขียน f-string ได้เอง โดยไม่ลืมตัว f หน้าเครื่องหมายคำพูด</li>
    <li>จัดตัวเลขให้มีลูกน้ำและทศนิยม 2 ตำแหน่งด้วย <code>:,.2f</code> ได้</li>
    <li>โปรแกรมใบเสร็จของคุณรันได้ครบ และตัวเลขในคอลัมน์เรียงตรงกันสวยงาม</li>
  </ul>
</div>

<h2>EP หน้าเจออะไร</h2>

<p>โปรแกรมของเราตอนนี้รับข้อมูลได้ คำนวณได้ แสดงผลสวยได้แล้ว
แต่มันยังทำเหมือนเดิมทุกครั้งไม่ว่าข้อมูลจะเป็นยังไง — ซื้อ 100 บาทกับซื้อ 100,000 บาท ก็ปฏิบัติเหมือนกัน</p>

<p>EP4 เราจะสอนให้โปรแกรม<b>ตัดสินใจเองได้</b> ปลายทางคือ
<b>ระบบให้ส่วนลดอัตโนมัติตามยอดซื้อ</b> ที่คิดให้เองว่าลูกค้าคนนี้ควรได้ลดกี่เปอร์เซ็นต์ครับ</p>
"""


# ===================================================================
# EP4
# ===================================================================
EP4 = """
<p>ทุกธุรกิจมีกฎอยู่ในหัวเจ้าของเสมอครับ "ซื้อครบพันลดห้าเปอร์เซ็นต์" "สมาชิกลดเพิ่มอีกห้า"
"ถ้าเงินไม่พอห้ามจบบิล" — กฎพวกนี้แหละที่เราจะย้ายจากหัวคุณลงไปอยู่ในโปรแกรม
พอย้ายเสร็จ โปรแกรมจะตัดสินใจแทนคุณได้เอง ไม่มีวันลืม ไม่มีวันคิดผิด</p>

<div class="callout c-tip">
  <span class="ico">🎯</span>
  <p><span class="ttl">จบ EP นี้คุณจะทำอะไรได้</span>
  เขียนเงื่อนไข if / elif / else ได้ · ใช้ and และ or รวมหลายเงื่อนไขได้ ·
  <b>เขียนระบบให้ส่วนลดอัตโนมัติตามยอดซื้อได้ 1 ตัว</b><br>
  <b>ใช้เวลา:</b> อ่าน 16 นาที + ลงมือทำ 30 นาที · <b>ต้องผ่านมาก่อน:</b> EP1-EP3</p>
</div>

<p><b>ทบทวน 30 วินาที</b> — EP3 เรารับค่าจากผู้ใช้ด้วย <code>input()</code>
แปลงชนิดด้วย <code>int()</code> / <code>float()</code> และจัดข้อความสวยๆ ด้วย f-string
โดยเฉพาะ <code>{total:,.2f}</code> ที่จะใช้ต่อใน EP นี้เยอะมาก</p>

<h2>if — ถ้าเงื่อนไขจริง ให้ทำ</h2>

<div class="analogy">
  <span class="emoji">🚦</span>
  <p>เหมือนป้ายหน้าร้านที่เขียนว่า <b>"ซื้อครบ 1,000 บาท รับส่วนลด 5%"</b>
  พนักงานของคุณจะดูยอดก่อน ถ้าถึงพันก็ลดให้ ถ้าไม่ถึงก็ไม่ลด
  <code>if</code> คือการเขียนป้ายนั้นให้คอมพิวเตอร์อ่านออกครับ</p>
</div>

<p>โครงสร้างมี 3 ส่วนที่ต้องครบ ขาดอย่างใดอย่างหนึ่งไม่ได้</p>

<pre><code>total = 1500

if total &gt;= 1000:              # 1. เงื่อนไข ตามด้วยเครื่องหมาย :
    print("คุณได้ส่วนลด 5%")    # 2. เว้น 4 ช่อง แล้วเขียนสิ่งที่จะทำ

print("จบการคำนวณ")             # 3. ชิดซ้าย = ทำทุกครั้งไม่ว่ายังไง</code></pre>

<p>ผลที่ได้คือทั้งสองบรรทัดถูกพิมพ์ แต่ถ้าเปลี่ยน <code>total</code> เป็น 500
จะเหลือแค่ "จบการคำนวณ" บรรทัดเดียว</p>

<figure>
  __SVG_INDENT__
  <figcaption>ใน Python การเว้นวรรคหน้าบรรทัดไม่ใช่แค่ความสวยงาม แต่มีความหมายจริงๆ</figcaption>
</figure>

<div class="callout c-danger">
  <span class="ico">🚫</span>
  <p><span class="ttl">การเว้นวรรคหน้าบรรทัดคือกฎเหล็กของ Python</span>
  ภาษาอื่นใช้ปีกกา { } บอกขอบเขต แต่ Python ใช้<b>การย่อหน้า</b>แทน
  บรรทัดที่ย่อหน้าเข้าไปคือ "อยู่ในเงื่อนไข" บรรทัดที่ชิดซ้ายคือ "อยู่นอกเงื่อนไข"
  มาตรฐานคือ<b>เว้น 4 ช่อง</b> ซึ่ง VS Code จะทำให้อัตโนมัติเมื่อคุณกด Enter หลังเครื่องหมาย :</p>
</div>

<h2>เครื่องหมายเปรียบเทียบ 6 ตัว</h2>

<p>สิ่งที่อยู่หลัง <code>if</code> ต้องเป็นคำถามที่ตอบได้แค่ จริง หรือ เท็จ เท่านั้น
(จำ <code>bool</code> จาก EP2 ได้ไหมครับ — นี่แหละที่มันถูกใช้จริง)</p>

<pre><code>a = 10
b = 3

print(a &gt; b)      # True   มากกว่า
print(a &lt; b)      # False  น้อยกว่า
print(a &gt;= 10)    # True   มากกว่าหรือเท่ากับ
print(a &lt;= 9)     # False  น้อยกว่าหรือเท่ากับ
print(a == 10)    # True   เท่ากับ  (เท่ากับ 2 ตัว!)
print(a != b)     # True   ไม่เท่ากับ</code></pre>

<div class="callout c-warn">
  <span class="ico">⚠️</span>
  <p><span class="ttl">= กับ == ไม่เหมือนกันเด็ดขาด</span>
  <code>=</code> ตัวเดียว คือ <b>"เอาค่าใส่กล่อง"</b> (จาก EP2)<br>
  <code>==</code> สองตัว คือ <b>"ถามว่าเท่ากันไหม"</b><br>
  เขียน <code>if a = 10:</code> จะได้ <code>SyntaxError</code> ทันที
  เป็นความผิดพลาดที่คนเขียนโปรแกรมทุกคนบนโลกเคยทำ รวมถึงคนที่เขียนมา 20 ปีแล้วครับ</p>
</div>

<h2>else และ elif — ไล่เงื่อนไขเป็นชั้น</h2>

<p><code>else</code> แปลว่า "ถ้าไม่เข้าเงื่อนไขข้างบนเลย ให้ทำอันนี้แทน"</p>

<pre><code>total = 500

if total &gt;= 1000:
    print("ได้ส่วนลด")
else:
    print("ยังไม่ถึงยอดขั้นต่ำ ซื้อเพิ่มอีก", 1000 - total, "บาท")</code></pre>

<p>ส่วน <code>elif</code> (ย่อมาจาก else if) ใช้ตอนมีเงื่อนไขหลายชั้น ซึ่งเป็นกรณีของธุรกิจจริงส่วนใหญ่</p>

<pre><code>if total &gt;= 5000:
    discount = 0.15
elif total &gt;= 2000:
    discount = 0.10
elif total &gt;= 1000:
    discount = 0.05
else:
    discount = 0</code></pre>

<figure>
  __SVG_IF_FLOW__
  <figcaption>Python หยุดทันทีที่เจอเงื่อนไขแรกที่เป็นจริง ข้อที่เหลือไม่ถูกตรวจเลย</figcaption>
</figure>

<div class="callout c-danger">
  <span class="ico">🚫</span>
  <p><span class="ttl">ลำดับของ elif สำคัญมาก เรียงผิดคือธุรกิจเสียหายจริง</span>
  ถ้าคุณเอา <code>if total &gt;= 1000</code> ขึ้นก่อน ลูกค้าที่ซื้อ 8,000 บาท
  จะเข้าเงื่อนไขแรกทันทีแล้วได้ลดแค่ 5% ทั้งที่ควรได้ 15%
  เพราะ Python หยุดที่ข้อแรกที่จริง <b>กฎคือเรียงจากเงื่อนไขที่เข้มที่สุดลงมาหาหลวมที่สุดเสมอ</b></p>
</div>

<h2>and และ or — รวมหลายเงื่อนไข</h2>

<p>บางกฎต้องเช็คหลายอย่างพร้อมกัน เช่น "เป็นสมาชิก <b>และ</b> ซื้อครบ 1,000"</p>

<pre><code>is_member = True
total = 1500

if is_member and total &gt;= 1000:
    print("ได้ส่วนลดสมาชิกพิเศษ")</code></pre>

<ul>
  <li><code>and</code> — ต้องจริง<b>ทั้งคู่</b> ถึงจะผ่าน (เข้มกว่า)</li>
  <li><code>or</code> — จริง<b>อย่างใดอย่างหนึ่ง</b>ก็ผ่าน (หลวมกว่า)</li>
  <li><code>not</code> — กลับผลจากจริงเป็นเท็จ</li>
</ul>

<pre><code>if is_member or total &gt;= 5000:
    print("ส่งฟรี")           # เป็นสมาชิก หรือ ซื้อเยอะ อย่างใดอย่างหนึ่งก็ได้</code></pre>

<h2>สร้างระบบส่วนลดอัตโนมัติ</h2>

<p>รวมทุกอย่างเข้าด้วยกันครับ สร้างไฟล์ <code>ep4_discount.py</code></p>

<pre><code>print("=== ระบบคิดส่วนลด ร้านกาแฟหนูดี ===")
print()

total = float(input("ยอดซื้อรวม (บาท): "))
answer = input("เป็นสมาชิกไหม (y/n): ")
is_member = answer == "y"

# ==== ขั้นบันไดส่วนลดตามยอดซื้อ (เรียงจากเข้มไปหลวม) ====
if total &gt;= 5000:
    discount = 0.15
    tier = "ลูกค้า VIP"
elif total &gt;= 2000:
    discount = 0.10
    tier = "ลูกค้าประจำ"
elif total &gt;= 1000:
    discount = 0.05
    tier = "ลูกค้าทั่วไป"
else:
    discount = 0
    tier = "ยังไม่ถึงยอดขั้นต่ำ"

# ==== สมาชิกได้เพิ่มอีก 5% ====
if is_member:
    discount = discount + 0.05

# ==== คำนวณ ====
saved = total * discount
final = total - saved

# ==== แสดงผล ====
print()
print("=" * 38)
print(f"ระดับลูกค้า : {tier}")
if is_member:
    print("สถานะ       : สมาชิก (+5%)")
print("-" * 38)
print(f"ยอดซื้อ      : {total:>14,.2f} บาท")
print(f"ส่วนลด {discount*100:.0f}%   : {saved:>14,.2f} บาท")
print(f"ยอดต้องชำระ  : {final:>14,.2f} บาท")
print("=" * 38)

if discount == 0:
    need = 1000 - total
    print(f"ซื้อเพิ่มอีก {need:,.2f} บาท จะได้ส่วนลด 5% ทันที")</code></pre>

<p>ลองรันด้วยยอด 3,500 บาท และตอบว่าเป็นสมาชิก จะได้</p>

<pre><code>ยอดซื้อรวม (บาท): 3500
เป็นสมาชิกไหม (y/n): y

======================================
ระดับลูกค้า : ลูกค้าประจำ
สถานะ       : สมาชิก (+5%)
--------------------------------------
ยอดซื้อ      :       3,500.00 บาท
ส่วนลด 15%   :         525.00 บาท
ยอดต้องชำระ  :       2,975.00 บาท
======================================</code></pre>

<p>ลองรันซ้ำหลายๆ รอบด้วยยอดต่างกันครับ — 500, 1200, 2500, 8000 ทั้งแบบสมาชิกและไม่ใช่
คุณจะเห็นว่าโปรแกรมตัดสินใจถูกทุกครั้ง ไม่มีวันลืมกฎข้อไหนเลย
<b>นี่คือความต่างระหว่างกฎที่อยู่ในหัวคน กับกฎที่อยู่ในระบบ</b></p>

<div class="callout c-tip">
  <span class="ico">🏪</span>
  <p><span class="ttl">เอาไปใช้จริงได้เลย</span>
  เปลี่ยนตัวเลขขั้นบันไดกับเปอร์เซ็นต์ให้ตรงกับกฎร้านคุณ แล้วเปิดโปรแกรมนี้ทิ้งไว้ตอนคิดเงิน
  พนักงานใหม่จะคิดส่วนลดถูกตั้งแต่วันแรก โดยไม่ต้องท่องกฎเลยครับ</p>
</div>

<h2>กับดักที่คุณจะเจอ</h2>

<div class="callout c-danger">
  <span class="ico">🚫</span>
  <p><span class="ttl">1. ลืมเครื่องหมาย : ท้ายบรรทัด if</span>
  <code>if total &gt;= 1000</code> (ไม่มี :) จะได้
  <code>SyntaxError: expected ':'</code> — ทุกบรรทัดที่ขึ้นต้นด้วย if, elif, else
  ต้องจบด้วยเครื่องหมาย : เสมอ ไม่มีข้อยกเว้น</p>
</div>

<div class="callout c-danger">
  <span class="ico">🚫</span>
  <p><span class="ttl">2. ย่อหน้าไม่เท่ากัน</span>
  ถ้าบางบรรทัดเว้น 4 ช่อง บางบรรทัดเว้น 2 ช่อง จะได้
  <code>IndentationError: unindent does not match any outer indentation level</code>
  ปัญหานี้เกิดบ่อยเวลาก๊อปโค้ดจากเว็บมาวาง —
  <b>อีกเหตุผลที่ผมย้ำให้พิมพ์เอง</b> ถ้าเจอให้ลบช่องว่างหน้าบรรทัดทิ้งแล้วกด Tab ใหม่</p>
</div>

<div class="callout c-warn">
  <span class="ico">⚠️</span>
  <p><span class="ttl">3. เทียบข้อความโดยลืมเรื่องตัวพิมพ์ใหญ่-เล็ก</span>
  ถ้าคนใช้พิมพ์ <code>Y</code> ตัวใหญ่ แต่โค้ดคุณเช็ค <code>== "y"</code> ตัวเล็ก จะไม่ผ่าน
  แก้ได้ด้วย <code>answer.lower() == "y"</code> ซึ่ง <code>.lower()</code> จะแปลงเป็นตัวเล็กทั้งหมดก่อนเทียบ</p>
</div>

<div class="callout c-warn">
  <span class="ico">⚠️</span>
  <p><span class="ttl">4. ใช้ if หลายอันแทน elif</span>
  ถ้าเขียน <code>if</code> เรียงกัน 4 อันโดยไม่ใช้ <code>elif</code>
  Python จะตรวจทุกข้อและทำทุกข้อที่จริง ทำให้ลูกค้าที่ซื้อ 8,000 บาท
  โดนคิดส่วนลดทับกัน 3 ชั้น — จำง่ายๆ ว่า <b>เลือกได้แค่ข้อเดียวใช้ elif
  เลือกได้หลายข้อใช้ if แยก</b></p>
</div>

<h2>ลงมือทำ</h2>

<p><b>ข้อ 1 (ง่าย)</b> — เขียนโปรแกรมถามอายุ แล้วบอกว่าเข้าเงื่อนไขไหน
ต่ำกว่า 13 = เด็ก, 13-19 = วัยรุ่น, 20-59 = ผู้ใหญ่, 60 ขึ้นไป = ผู้สูงอายุ (ได้ส่วนลด 10%)</p>

<details __DET__>
  <summary __SUM__>ดูเฉลยข้อ 1</summary>
  <pre><code>age = int(input("อายุ: "))

if age &gt;= 60:
    print("ผู้สูงอายุ — รับส่วนลด 10%")
elif age &gt;= 20:
    print("ผู้ใหญ่")
elif age &gt;= 13:
    print("วัยรุ่น")
else:
    print("เด็ก")</code></pre>
  <p style="margin-top:0.7rem;">สังเกตว่าเรียงจากมากไปน้อย ทำให้ไม่ต้องเขียนเงื่อนไขซ้อนแบบ
  <code>age &gt;= 20 and age &lt; 60</code> เลย เพราะถ้ามาถึงบรรทัดนั้นได้ แปลว่าไม่ถึง 60 อยู่แล้ว</p>
</details>

<p><b>ข้อ 2 (กลาง)</b> — แก้โปรแกรมเงินทอนจาก EP3 ให้เตือนเมื่อลูกค้าให้เงินไม่พอ
และบอกว่าขาดอีกเท่าไหร่ ถ้าพอดีเป๊ะให้บอกว่า "รับเงินพอดี ไม่มีทอน"</p>

<details __DET__>
  <summary __SUM__>ดูเฉลยข้อ 2</summary>
  <pre><code>total = float(input("ยอดที่ต้องจ่าย: "))
paid = float(input("ลูกค้าให้มา: "))

if paid &lt; total:
    short = total - paid
    print(f"เงินไม่พอครับ ขาดอีก {short:,.2f} บาท")
elif paid == total:
    print("รับเงินพอดี ไม่มีทอน")
else:
    change = paid - total
    print(f"เงินทอน {change:,.2f} บาท")</code></pre>
</details>

<p><b>ข้อ 3 (ท้าทาย)</b> — ร้านมีโปรโมชั่นส่งฟรีเมื่อ "ซื้อครบ 500 บาท <b>หรือ</b> เป็นสมาชิก"
แต่ถ้าอยู่ต่างจังหวัดต้องซื้อครบ 1,000 บาทถึงจะส่งฟรี เขียนโปรแกรมตัดสินใจให้</p>

<details __DET__>
  <summary __SUM__>ดูเฉลยข้อ 3</summary>
  <pre><code>total = float(input("ยอดซื้อ: "))
is_member = input("เป็นสมาชิกไหม (y/n): ").lower() == "y"
upcountry = input("อยู่ต่างจังหวัดไหม (y/n): ").lower() == "y"

if upcountry:
    limit = 1000
else:
    limit = 500

if total &gt;= limit or is_member:
    print("ส่งฟรีครับ")
else:
    need = limit - total
    print(f"ค่าส่ง 50 บาท — ซื้อเพิ่มอีก {need:,.2f} บาท ส่งฟรีทันที")</code></pre>
  <p style="margin-top:0.7rem;">เทคนิคสำคัญคือ<b>แยกการตัดสินใจเป็น 2 ขั้น</b> —
  ขั้นแรกหาว่ายอดขั้นต่ำของลูกค้าคนนี้คือเท่าไหร่ ขั้นสองค่อยเช็คว่าถึงหรือยัง
  ถ้ายัดทุกอย่างไว้ใน if เดียวจะอ่านยากมากและแก้ทีหลังไม่ได้เลย</p>
</details>

<h2>เช็คว่าคุณผ่าน EP นี้จริง</h2>

<div class="checklist">
  <ul>
    <li>อธิบายความต่างของ <code>=</code> กับ <code>==</code> ได้</li>
    <li>บอกได้ว่าทำไมลำดับของ <code>elif</code> ถึงสำคัญ และเรียงผิดแล้วเกิดอะไรขึ้น</li>
    <li>เว้นวรรคหน้าบรรทัดถูกต้อง ไม่เจอ <code>IndentationError</code> อีกแล้ว</li>
    <li>ระบบส่วนลดของคุณรันได้ และทดสอบด้วยยอด 500 / 1,200 / 3,500 / 8,000 แล้วผลถูกทุกกรณี</li>
  </ul>
</div>

<div class="callout c-tip">
  <span class="ico">🎉</span>
  <p><span class="ttl">คุณจบช่วงที่ 1 แล้ว</span>
  ถึงตรงนี้คุณสั่งคอมพิวเตอร์ให้รับข้อมูล คำนวณ ตัดสินใจ และแสดงผลได้ครบวงจรแล้วครับ
  นี่คือ 4 อย่างที่โปรแกรมทุกตัวบนโลกทำ ไม่ว่าจะเป็นแอปธนาคารหรือเกมมือถือ —
  ต่างกันแค่ความซับซ้อนเท่านั้น</p>
</div>

<h2>EP หน้าเจออะไร</h2>

<p>ปัญหาที่คุณน่าจะเริ่มรู้สึกแล้วคือ ถ้าลูกค้ามี 50 คน คุณต้องรันโปรแกรม 50 รอบ
หรือถ้าบิลมี 20 รายการ ก็ต้องเขียนตัวแปร 20 ชุด — มันไปต่อไม่ไหวแน่นอน</p>

<p>EP5 เราจะเข้าสู่ช่วงที่ 2 ด้วยของสองอย่างที่จะเปลี่ยนวิธีเขียนโปรแกรมของคุณไปตลอดกาล
คือ <b>ลิสต์</b> (เก็บของหลายชิ้นในกล่องเดียว) และ <b>ลูป</b> (ทำซ้ำจนกว่าจะหมด)
ปลายทางคือโปรแกรมสรุปยอดขาย 50 บิลที่ทำงานเสร็จใน 1 วินาทีครับ</p>
"""


# ===================================================================
# ประกอบร่าง + เขียนลง DB
# ===================================================================
SVG_MAP = {
    "__SVG_HOW_PYTHON_RUNS__": SVG_HOW_PYTHON_RUNS,
    "__SVG_VARIABLE_BOX__": SVG_VARIABLE_BOX,
    "__SVG_DATA_TYPES__": SVG_DATA_TYPES,
    "__SVG_INPUT_FLOW__": SVG_INPUT_FLOW,
    "__SVG_IF_FLOW__": SVG_IF_FLOW,
    "__SVG_INDENT__": SVG_INDENT,
}


def build(raw):
    out = raw.replace("__DET__", DET).replace("__SUM__", SUM)
    for key, svg in SVG_MAP.items():
        out = out.replace(key, svg)
    return out.strip()


EPISODES = [
    {
        "slug": "python-101-ep1",
        "title": "EP1: ติดตั้ง Python และเขียนโค้ดบรรทัดแรก",
        "excerpt": "เริ่มจากศูนย์จริงๆ — ติดตั้ง Python กับ VS Code ลงเครื่อง สร้างไฟล์ .py แรกของคุณ "
                   "แล้วรันให้ขึ้นข้อความบนหน้าจอได้ภายใน 25 นาที พร้อมกับดัก 4 ข้อที่มือใหม่พลาดกันทุกคน",
        "meta_title": "EP1 ติดตั้ง Python และรันโค้ดบรรทัดแรก | คอร์ส Python เริ่มต้น",
        "meta_description": "สอนติดตั้ง Python และ VS Code ทีละขั้น พร้อมเขียนโค้ดบรรทัดแรกให้รันได้จริง "
                            "อธิบายทุกจุดที่มือใหม่มักพลาด เช่น ช่อง Add to PATH",
        "content": EP1,
    },
    {
        "slug": "python-101-ep2",
        "title": "EP2: ตัวแปรและชนิดข้อมูล — สร้างเครื่องคิดเลขคิดกำไรร้าน",
        "excerpt": "ให้โปรแกรมมีความจำด้วยตัวแปร รู้จักชนิดข้อมูล 4 แบบที่ใช้จริง 95% ของงาน "
                   "แล้วเขียนเครื่องคิดเลขคำนวณกำไรร้านตัวเองที่แก้ตัวเลขที่เดียวแล้วคิดต่อให้เองทั้งหมด",
        "meta_title": "EP2 ตัวแปรและชนิดข้อมูล Python พร้อมตัวอย่างคิดกำไรร้าน",
        "meta_description": "เข้าใจตัวแปร Python และชนิดข้อมูล str int float bool ผ่านตัวอย่างธุรกิจจริง "
                            "จบบทเขียนเครื่องคิดเลขคิดกำไรร้านได้เอง",
        "content": EP2,
    },
    {
        "slug": "python-101-ep3",
        "title": "EP3: รับค่าจากผู้ใช้และจัดข้อความ — เขียนโปรแกรมออกใบเสร็จ",
        "excerpt": "ทำให้โปรแกรมถามข้อมูลเองด้วย input() แก้กับดักอันดับ 1 ของมือใหม่เรื่องข้อความกับตัวเลข "
                   "และใช้ f-string จัดตัวเลขให้มีลูกน้ำกับทศนิยมสวยงามระดับใบเสร็จจริง",
        "meta_title": "EP3 input และ f-string ใน Python — เขียนโปรแกรมออกใบเสร็จ",
        "meta_description": "สอนใช้ input() รับค่าจากผู้ใช้ แปลงชนิดด้วย int float และจัดรูปแบบตัวเลข "
                            "ด้วย f-string จบบทได้โปรแกรมออกใบเสร็จพร้อม VAT",
        "content": EP3,
    },
    {
        "slug": "python-101-ep4",
        "title": "EP4: เงื่อนไข if/else — สร้างระบบส่วนลดอัตโนมัติ",
        "excerpt": "ย้ายกฎธุรกิจที่อยู่ในหัวคุณลงไปอยู่ในโปรแกรม สอน if elif else พร้อม and or "
                   "และกับดักเรื่องลำดับเงื่อนไขที่เรียงผิดแล้วธุรกิจเสียหายจริง จบบทได้ระบบคิดส่วนลดใช้งานได้ทันที",
        "meta_title": "EP4 เงื่อนไข if elif else ใน Python — ระบบส่วนลดอัตโนมัติ",
        "meta_description": "สอนเขียนเงื่อนไข if elif else และ and or ใน Python ผ่านระบบคิดส่วนลดร้านค้า "
                            "พร้อมอธิบายเรื่องการย่อหน้าและลำดับเงื่อนไข",
        "content": EP4,
    },
]

tag_names = ["Python", "สอนเขียนโปรแกรม", "คอร์สเรียน", "มือใหม่"]
tags = [Tag.objects.get_or_create(name=n)[0] for n in tag_names]

for ep in EPISODES:
    content = build(ep["content"])
    article, created = Article.objects.update_or_create(
        slug=ep["slug"],
        defaults={
            "title": ep["title"],
            "author": author,
            "category": category,
            "excerpt": ep["excerpt"],
            "content": content,
            # กลับไปโหมด HTML ชั่วคราว ไม่งั้น save() จะ render ทับจาก content_md เดิม
            "content_format": "html",
            "content_md": "",
            "meta_title": ep["meta_title"],
            "meta_description": ep["meta_description"],
            "status": "draft",
            "layout": "docs",
            "is_featured": False,
        },
    )
    article.tags.set(tags)
    print("%-8s id=%-4s %-6s %6d chars  %s" % (
        ep["slug"].replace("python-101-", ""),
        article.pk,
        "new" if created else "update",
        len(content),
        ep["title"][:52],
    ))

print()
print("เสร็จแล้ว — ทั้งหมดเป็น draft รอตรวจและกด publish")
