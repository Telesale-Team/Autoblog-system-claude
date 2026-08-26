# -*- coding: utf-8 -*-
r"""
สร้าง Category "Python สำหรับคนเริ่มต้น" + บทความ EP0 (หน้าปฐมนิเทศ/สารบัญคอร์ส)

- Category ใหม่แยกเฉพาะคอร์สนี้ slug=python-101 -> ทุก EP จะอยู่ในหมวดนี้หมด
- layout = "docs"  -> detail.html แสดง TOC อัตโนมัติ + สไตล์ docs + ซ่อน CTA ขายของ
- status = "draft" -> ผู้ใช้ตรวจแล้วกด publish เองใน Django admin เสมอ
- insert HTML ตรงเข้า DB (ไม่ผ่าน CKEditor) -> inline SVG / callout รอด ไม่โดน editor กิน

run: .\venv\Scripts\python.exe scripts\create_python101_ep0.py
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
if author is None:
    raise SystemExit("ไม่พบ user ใน DB — สร้าง superuser ก่อน")

# ===================================================================
# Category เฉพาะคอร์สนี้
# ===================================================================
category, cat_created = Category.objects.get_or_create(
    slug="python-101",
    defaults={
        "name": "Python สำหรับคนเริ่มต้น",
        "description": "คอร์สเรียนเขียนโปรแกรม Python จากศูนย์ 12 บทเรียน "
                       "สำหรับคนไม่เคยเขียนโค้ด เน้นตัวอย่างจากธุรกิจจริง",
        "color": "warning",
        "display_order": 1,
    },
)

# ===================================================================
# ไดอะแกรม roadmap 12 EP แบ่ง 3 ช่วง
# SVG ใช้ attribute styling (ไม่ใช้ <style> ใน svg) กันคลาสรั่วทั้งหน้า
# ===================================================================

def chip(x, y, no, label):
    return (
        f'<rect x="{x}" y="{y}" width="198" height="40" rx="9" fill="#111827" stroke="#1f2937"/>'
        f'<circle cx="{x + 24}" cy="{y + 20}" r="13" fill="rgba(201,169,110,0.12)" stroke="#c9a96e" stroke-opacity="0.55"/>'
        f'<text x="{x + 24}" y="{y + 25}" text-anchor="middle" font-family="Segoe UI,sans-serif" '
        f'font-size="11" font-weight="700" fill="#c9a96e">{no}</text>'
        f'<text x="{x + 46}" y="{y + 25}" font-family="Segoe UI,sans-serif" font-size="12.5" fill="#cbd5e1">{label}</text>'
    )


def phase(px, title, subtitle, items):
    out = (
        f'<rect x="{px}" y="45" width="230" height="272" rx="14" fill="#0f1626" stroke="#1f2937"/>'
        f'<text x="{px + 16}" y="72" font-family="Segoe UI,sans-serif" font-size="13.5" '
        f'font-weight="700" fill="#c9a96e">{title}</text>'
        f'<text x="{px + 16}" y="90" font-family="Segoe UI,sans-serif" font-size="11" fill="#94a3b8">{subtitle}</text>'
    )
    ys = [102, 150, 198, 246]
    for (no, label), y in zip(items, ys):
        out += chip(px + 16, y, no, label)
    return out


SVG_ROADMAP = (
    '<svg viewBox="0 0 760 340" role="img" '
    'aria-label="แผนที่คอร์ส Python 12 บทเรียน แบ่งเป็น 3 ช่วง: พื้นฐาน จัดการข้อมูล และของจริง" '
    'xmlns="http://www.w3.org/2000/svg">'
    '<text x="20" y="26" font-family="Segoe UI,sans-serif" font-size="14" font-weight="700" '
    'fill="#f1f5f9">เส้นทางเรียน 12 บทเรียน</text>'
    + phase(20, "ช่วงที่ 1 — พื้นฐาน", "สั่งคอมพิวเตอร์ให้ทำตามได้", [
        ("1", "ติดตั้ง + รันโค้ดแรก"),
        ("2", "ตัวแปร + ชนิดข้อมูล"),
        ("3", "รับค่า + จัดข้อความ"),
        ("4", "เงื่อนไข if/else"),
    ])
    + '<polygon points="252,180 264,187 252,194" fill="#c9a96e" fill-opacity="0.7"/>'
    + phase(265, "ช่วงที่ 2 — จัดการข้อมูล", "ทำงานกับข้อมูลจำนวนมาก", [
        ("5", "ลิสต์ + วนลูป for"),
        ("6", "Dictionary"),
        ("7", "ฟังก์ชัน"),
        ("8", "อ่าน/เขียนไฟล์ CSV"),
    ])
    + '<polygon points="497,180 509,187 497,194" fill="#c9a96e" fill-opacity="0.7"/>'
    + phase(510, "ช่วงที่ 3 — ของจริง", "เอาไปใช้กับงานตัวเอง", [
        ("9", "อ่าน error ให้เป็น"),
        ("10", "ติดตั้ง Library (pip)"),
        ("11", "เรียก API"),
        ("12", "Capstone: สรุปยอด → LINE"),
    ])
    + '</svg>'
)

# ===================================================================
# เนื้อหา EP0 (inner HTML — title/cover จัดการโดย template)
# ===================================================================
CONTENT = """
<p>ทุกสิ้นวันคุณเปิด Excel ขึ้นมานั่งบวกยอดขายทีละบิล ทุกสิ้นเดือนคุณก๊อปข้อมูลจากไฟล์หนึ่งไปวางอีกไฟล์หนึ่ง
ทุกเช้าคุณเปิด 5 แท็บเพื่อเช็คตัวเลขเดิมๆ — งานพวกนี้กินเวลาวันละ 20 นาที
ฟังดูน้อย แต่ปีหนึ่งคือ <b>120 ชั่วโมง</b> ที่หายไปกับงานที่คอมพิวเตอร์ทำแทนได้ทั้งหมด</p>

<p>คอร์สนี้ไม่ได้จะเปลี่ยนคุณเป็นโปรแกรมเมอร์ครับ แต่จะสอนให้คุณ<b>สั่งคอมพิวเตอร์ทำงานซ้ำๆ แทนคุณได้</b>
ด้วยภาษา Python — ภาษาที่อ่านแล้วเกือบเหมือนภาษาอังกฤษธรรมดา และเป็นภาษาที่มือใหม่เริ่มได้ง่ายที่สุดในตอนนี้</p>

<div class="analogy">
  <span class="emoji">🍳</span>
  <p>การเขียนโปรแกรมก็เหมือน<b>เขียนสูตรอาหารให้คนที่ทำตามเป๊ะมาก แต่ไม่คิดเอง</b>
  ถ้าคุณเขียนว่า "ใส่เกลือ" เขาจะใส่ทั้งถุง เพราะคุณไม่ได้บอกว่ากี่ช้อน
  ทั้งคอร์สนี้คือการฝึกเขียนสูตรให้ชัดจนคอมพิวเตอร์ทำตามได้ถูก</p>
</div>

<h2>คอร์สนี้เหมาะกับใคร</h2>

<p>ผมเขียนคอร์สนี้โดยคิดถึงคน 3 กลุ่มนี้เป็นหลักครับ</p>

<div class="step">
  <div class="step__n">1</div>
  <div class="step__body">
    <h3>เจ้าของธุรกิจ / คนทำงานออฟฟิศที่เบื่องานซ้ำ</h3>
    <p>คุณรู้ว่างานที่ทำอยู่มันน่าจะทำอัตโนมัติได้ แต่ไม่รู้จะเริ่มตรงไหน — เริ่มที่นี่ครับ</p>
  </div>
</div>

<div class="step">
  <div class="step__n">2</div>
  <div class="step__body">
    <h3>คนที่เคยลองเรียนเขียนโค้ดแล้วเลิกกลางคัน</h3>
    <p>ส่วนใหญ่เลิกเพราะเรียนไป 3 บทแล้วยังไม่รู้ว่าจะเอาไปทำอะไร คอร์สนี้ทุกบทจบด้วยโปรแกรมที่ใช้ได้จริง 1 ตัว</p>
  </div>
</div>

<div class="step">
  <div class="step__n">3</div>
  <div class="step__body">
    <h3>คนที่อยากคุยกับ AI ให้เขียนโค้ดให้รู้เรื่อง</h3>
    <p>ทุกวันนี้ AI เขียนโค้ดให้ได้ แต่ถ้าคุณอ่านโค้ดไม่ออกเลย คุณจะไม่รู้ว่ามันเขียนถูกหรือผิด
    คอร์สนี้ทำให้คุณ<b>ตรวจงาน AI เป็น</b></p>
  </div>
</div>

<div class="callout c-warn">
  <span class="ico">⚠️</span>
  <p><span class="ttl">คอร์สนี้ไม่เหมาะกับใคร</span>
  ถ้าคุณเขียน Python เป็นอยู่แล้ว หรืออยากได้คอร์สที่ลงลึกเรื่อง Data Science / Machine Learning โดยตรง
  คอร์สนี้จะช้าเกินไปสำหรับคุณครับ — เริ่มที่ EP8 เป็นต้นไปแทน</p>
</div>

<h2>จบคอร์สแล้วคุณจะทำอะไรได้</h2>

<p>ปลายทางของคอร์สนี้ไม่ใช่ใบประกาศ แต่เป็น<b>โปรแกรมจริง 1 ตัวที่คุณเขียนเองและใช้ทุกวัน</b></p>

<div class="callout c-tip">
  <span class="ico">🎯</span>
  <p><span class="ttl">ผลงานปลายคอร์ส (EP12)</span>
  โปรแกรมที่เปิดไฟล์ยอดขายของร้านคุณ → คำนวณยอดรวม สินค้าขายดี และเทียบกับเมื่อวาน →
  ส่งสรุปเข้า LINE ให้คุณทุกเย็นอัตโนมัติ โดยคุณไม่ต้องแตะอะไรเลย</p>
</div>

<p>ระหว่างทางคุณจะได้โปรแกรมเล็กๆ อีก 11 ตัว ตั้งแต่เครื่องคิดเลขคิดกำไร ไปจนถึงโปรแกรมอ่านไฟล์ Excel
ทุกตัวเก็บไว้ใช้ต่อได้จริง ไม่ใช่โค้ดฝึกหัดที่เขียนเสร็จแล้วทิ้ง</p>

<h2>แผนที่คอร์ส — 12 บทเรียน 3 ช่วง</h2>

<figure>
  __SVG_ROADMAP__
  <figcaption>เส้นทางเรียนทั้งหมด — แต่ละช่วงต่อยอดจากช่วงก่อนหน้า ห้ามข้าม</figcaption>
</figure>

<p><b>ช่วงที่ 1 (EP1-4) พื้นฐาน</b> — เรียนรู้วิธีสั่งคอมพิวเตอร์ให้ทำตาม
จบช่วงนี้คุณจะเขียนโปรแกรมคิดเงินลูกค้าพร้อมส่วนลดอัตโนมัติได้</p>

<p><b>ช่วงที่ 2 (EP5-8) จัดการข้อมูล</b> — จากที่ทำงานกับข้อมูลทีละชิ้น เปลี่ยนเป็นทำกับข้อมูลทีละร้อยชิ้น
จบช่วงนี้คุณจะเปิดไฟล์ยอดขายจาก Excel มาประมวลผลได้เอง</p>

<p><b>ช่วงที่ 3 (EP9-12) ของจริง</b> — ช่วงที่คอร์สฟรีทั่วไปไม่ค่อยสอน
ทั้งการแก้บั๊กด้วยตัวเอง การหยิบเครื่องมือที่คนอื่นเขียนไว้แล้วมาใช้ และการดึงข้อมูลจากอินเทอร์เน็ต</p>

<h2>ต้องเตรียมอะไรบ้าง</h2>

<p>ข่าวดีคือแทบไม่ต้องเตรียมอะไรเลยครับ ไม่ต้องซื้ออะไรสักบาท</p>

<div class="checklist">
  <ul>
    <li>คอมพิวเตอร์ 1 เครื่อง — Windows, Mac หรือ Linux ก็ได้ เครื่องเก่าก็ได้ ไม่ต้องแรง</li>
    <li>อินเทอร์เน็ต — ใช้ตอนติดตั้งโปรแกรมใน EP1 เท่านั้น หลังจากนั้นเรียนออฟไลน์ได้</li>
    <li>เวลาว่างประมาณ 45 นาทีต่อบทเรียน (อ่าน 15 นาที + ลงมือทำ 30 นาที)</li>
    <li>สมุดหรือไฟล์โน้ต 1 อัน — จดคำสั่งที่ใช้บ่อย จะช่วยได้มากในช่วงแรก</li>
  </ul>
</div>

<div class="callout c-note">
  <span class="ico">💡</span>
  <p><span class="ttl">ไม่ต้องมีพื้นฐานอะไรเลย</span>
  ไม่ต้องเก่งเลข ไม่ต้องเก่งอังกฤษ ไม่ต้องเคยเรียนคอมพิวเตอร์มาก่อน
  ขอแค่ใช้คอมพิวเตอร์พื้นฐานเป็น — เปิดโฟลเดอร์ ติดตั้งโปรแกรม พิมพ์ไทย-อังกฤษได้ ก็พอแล้วครับ</p>
</div>

<h2>วิธีเรียนให้จบจริง</h2>

<p>สถิติของคอร์สออนไลน์ทั่วโลกคือมีคนเรียนจบไม่ถึง 15% ผมอยากให้คุณอยู่ในกลุ่มที่จบครับ
จากประสบการณ์ มี 3 อย่างที่ทำให้คนเรียนจบต่างจากคนที่เลิกกลางทาง</p>

<div class="step">
  <div class="step__n">1</div>
  <div class="step__body">
    <h3>พิมพ์โค้ดเอง อย่าก๊อปวาง</h3>
    <p>ฟังดูเสียเวลา แต่การพิมพ์เองทำให้คุณเจอ error และการเจอ error คือการเรียนรู้ที่แท้จริง
    คนที่ก๊อปวางตลอดจะรู้สึกว่าเข้าใจ แต่พอเขียนเองจริงจะเขียนไม่ออก</p>
  </div>
</div>

<div class="step">
  <div class="step__n">2</div>
  <div class="step__body">
    <h3>ทำโจทย์ท้ายบททุกบท อย่างน้อยข้อแรก</h3>
    <p>ทุก EP มีโจทย์ 3 ข้อ ง่าย-กลาง-ท้าทาย ถ้าไม่มีเวลาจริงๆ ขอแค่ข้อแรกข้อเดียวก็ยังดี
    การอ่านอย่างเดียวโดยไม่ลงมือ เท่ากับดูคนอื่นออกกำลังกายแล้วหวังว่าตัวเองจะแข็งแรง</p>
  </div>
</div>

<div class="step">
  <div class="step__n">3</div>
  <div class="step__body">
    <h3>อย่ารีบ และอย่าข้าม</h3>
    <p>แต่ละ EP ต่อยอดจาก EP ก่อนหน้าโดยตรง ถ้าอ่าน EP5 แล้วงง ให้กลับไปอ่าน EP4 ใหม่
    ไม่ใช่ความผิดคุณ แปลว่าฐานยังไม่แน่นพอเท่านั้นเอง สัปดาห์ละ 1 EP คือจังหวะที่กำลังดี</p>
  </div>
</div>

<div class="callout c-danger">
  <span class="ico">🚫</span>
  <p><span class="ttl">กับดักที่เจอบ่อยที่สุด</span>
  "ขอดูให้จบทั้งคอร์สก่อน แล้วค่อยกลับมาลงมือทำทีเดียว" — วิธีนี้ไม่เคยได้ผลครับ
  เพราะพอถึงเวลาลงมือจริง คุณจะลืมของ EP1 ไปหมดแล้ว อ่านจบ 1 บท ลงมือทำ 1 บท เสมอ</p>
</div>

<h2>พร้อมแล้วเริ่มกันเลย</h2>

<p>EP1 เราจะติดตั้ง Python ลงเครื่องคุณ และเขียนโค้ดบรรทัดแรกให้รันได้จริงภายใน 20 นาที
ไม่มีทฤษฎียาวๆ ไม่มีศัพท์เทคนิคที่ยังไม่จำเป็น — เปิดเครื่อง แล้วทำตามไปพร้อมกันเลยครับ</p>

<div class="callout c-tip">
  <span class="ico">🐶</span>
  <p><span class="ttl">จากหนูดี</span>
  ผมจะอยู่เป็นเพื่อนคุณตลอด 12 บทเรียนนี้ครับ ถ้าติดตรงไหน อ่านซ้ำแล้วยังไม่เข้าใจ
  ทักมาที่ LINE ได้เลย ไม่มีคำถามไหนโง่เกินไปสำหรับคนที่เพิ่งเริ่มครับ</p>
</div>
"""

CONTENT = CONTENT.replace("__SVG_ROADMAP__", SVG_ROADMAP).strip()

# ===================================================================
# สร้าง / อัปเดต บทความ EP0
# ===================================================================
SLUG = "python-101-ep0"

# ถ้าบทความมีอยู่แล้ว ให้คงสถานะเดิมไว้ (ห้าม downgrade published -> draft เอง)
existing = Article.objects.filter(slug=SLUG).first()
keep_status = existing.status if existing else "draft"

article, created = Article.objects.update_or_create(
    slug=SLUG,
    defaults={
        "title": "EP0: คอร์ส Python สำหรับคนเริ่มต้น — เขียนโปรแกรมให้ทำงานแทนเรา",
        "author": author,
        "category": category,
        "excerpt": "คอร์สเรียน Python จากศูนย์ 12 บทเรียน สำหรับคนไม่เคยเขียนโค้ดเลย "
                   "ทุกบทจบด้วยโปรแกรมที่ใช้ได้จริง ปลายทางคือระบบสรุปยอดขายส่งเข้า LINE อัตโนมัติ",
        "content": CONTENT,
        # กลับไปโหมด HTML ชั่วคราว ไม่งั้น save() จะ render ทับจาก content_md เดิม
        "content_format": "html",
        "content_md": "",
        "meta_title": "คอร์ส Python สำหรับคนเริ่มต้น 12 บทเรียน (ฟรี) | Noodee BootBiz",
        "meta_description": "เรียน Python จากศูนย์ 12 บทเรียน สำหรับคนไม่เคยเขียนโค้ด "
                            "ตัวอย่างจากธุรกิจจริง จบแล้วเขียนโปรแกรมสรุปยอดขายส่ง LINE ได้เอง",
        "status": keep_status,
        "layout": "docs",
        "is_featured": False,
    },
)

tag_names = ["Python", "สอนเขียนโปรแกรม", "คอร์สเรียน", "มือใหม่"]
tags = []
for name in tag_names:
    tag, _ = Tag.objects.get_or_create(name=name)
    tags.append(tag)
article.tags.set(tags)

print("Category :", category.name, "/", category.slug, "(created)" if cat_created else "(existing)")
print("Article  :", "created" if created else "updated", "| id =", article.pk)
print("Title    :", article.title)
print("Status   :", article.status, "| layout =", article.layout)
print("Preview  : http://127.0.0.1:8000/blog/%s/" % article.slug)
print("Content  :", len(CONTENT), "chars")
