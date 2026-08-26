# -*- coding: utf-8 -*-
r"""
สร้าง Article docs prototype — แปลง Guide 01 เป็นบทความ docs จริงในบล็อก (draft)
- layout = "docs"  -> detail.html จะแสดง TOC อัตโนมัติ + สไตล์ docs + ซ่อน CTA ขายของ
- insert HTML ตรงเข้า DB (ไม่ผ่าน CKEditor) -> inline SVG / callout รอด ไม่โดน editor กิน
run: .\venv\Scripts\python.exe scripts\create_docs_prototype.py
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
from blog.models import Article, Category

User = get_user_model()

# ---- author: superuser คนแรก หรือ user คนแรก ----
author = User.objects.filter(is_superuser=True).first() or User.objects.first()
if author is None:
    raise SystemExit("ไม่พบ user ใน DB — สร้าง superuser ก่อน")

# ---- category: คู่มือ / Docs ----
category, _ = Category.objects.get_or_create(
    name="คู่มือ / Docs",
    defaults={"description": "เอกสารอ่านเก็บไว้ สไตล์ docs เล่าเรื่อง", "color": "info", "display_order": 5},
)

# ===================================================================
# เนื้อหา docs (inner HTML — title/cover จัดการโดย template)
# ใช้คลาส: analogy / callout c-* / step / figure / checklist
# SVG ใช้ attribute styling (ไม่ใช้ <style> ใน svg) กันคลาสรั่วทั้งหน้า
# ===================================================================

SVG_WHERE = '''
<svg viewBox="0 0 760 360" role="img" aria-label="ไดอะแกรมแสดงตำแหน่งไฟล์ของทีม" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="30" width="430" height="300" rx="14" fill="#0f1626" stroke="#1f2937"/>
  <text x="40" y="58" font-family="Segoe UI,sans-serif" font-size="14" font-weight="700" fill="#f1f5f9">📁 โฟลเดอร์โปรเจกต์</text>
  <text x="40" y="76" font-family="Consolas,monospace" font-size="12" fill="#94a3b8">My-New-Project/</text>
  <rect x="44" y="92" width="382" height="150" rx="10" fill="#111827" stroke="#c9a96e" stroke-opacity="0.5"/>
  <text x="60" y="116" font-family="Segoe UI,sans-serif" font-size="13" font-weight="700" fill="#c9a96e">📂 .claude/</text>
  <text x="74" y="140" font-family="Segoe UI,sans-serif" font-size="13" fill="#cbd5e1">agents/ — Agent ทั้ง 25 ตัว (หนูดี + ทีม)</text>
  <text x="74" y="164" font-family="Segoe UI,sans-serif" font-size="13" fill="#cbd5e1">skills/ — ความสามารถ 12 skill</text>
  <text x="74" y="188" font-family="Segoe UI,sans-serif" font-size="13" fill="#cbd5e1">settings.json — hooks + permission</text>
  <text x="74" y="212" font-family="Segoe UI,sans-serif" font-size="13" fill="#cbd5e1">startup_hook.py — โปรโตคอลเปิดงาน</text>
  <rect x="44" y="256" width="382" height="50" rx="10" fill="#111827" stroke="#1f2937"/>
  <text x="60" y="286" font-family="Segoe UI,sans-serif" font-size="13" font-weight="700" fill="#c9a96e">📄 CLAUDE.md — คู่มือ + routing logic</text>
  <rect x="500" y="110" width="240" height="140" rx="14" fill="#0f1626" stroke="#f59e0b" stroke-dasharray="6 5"/>
  <text x="520" y="138" font-family="Segoe UI,sans-serif" font-size="14" font-weight="700" fill="#f1f5f9">🧠 memory/</text>
  <text x="520" y="160" font-family="Segoe UI,sans-serif" font-size="11" fill="#94a3b8">ความทรงจำถาวร</text>
  <text x="520" y="182" font-family="Segoe UI,sans-serif" font-size="11" fill="#94a3b8">MEMORY.md + ไฟล์ความจำ</text>
  <rect x="520" y="198" width="200" height="36" rx="8" fill="rgba(245,158,11,0.08)" stroke="rgba(245,158,11,0.4)"/>
  <text x="534" y="221" font-family="Segoe UI,sans-serif" font-size="11" fill="#fbbf24">⚠ อยู่ "นอก" โปรเจกต์</text>
  <line x1="450" y1="180" x2="500" y2="180" stroke="#f59e0b" stroke-width="2" stroke-dasharray="5 4"/>
  <polygon points="500,180 491,175 491,185" fill="#f59e0b"/>
  <text x="453" y="172" font-family="Segoe UI,sans-serif" font-size="11" fill="#fbbf24">ผูกด้วย path</text>
</svg>'''

SVG_MEMORY = '''
<svg viewBox="0 0 760 290" role="img" aria-label="ไดอะแกรมแสดงว่าทำไมความจำหายเมื่อเปลี่ยน path" xmlns="http://www.w3.org/2000/svg">
  <rect x="20" y="30" width="240" height="60" rx="10" fill="#0f1626" stroke="#1f2937"/>
  <text x="36" y="54" font-family="Segoe UI,sans-serif" font-size="13" font-weight="700" fill="#cbd5e1">path โปรเจกต์เดิม</text>
  <text x="36" y="76" font-family="Consolas,monospace" font-size="12" fill="#64748b">...Agent-Skill-Claude/</text>
  <text x="286" y="65" font-family="Segoe UI,sans-serif" font-size="14" font-weight="700" fill="#64748b">→</text>
  <rect x="320" y="30" width="180" height="60" rx="10" fill="#111827" stroke="#1f2937"/>
  <text x="336" y="54" font-family="Segoe UI,sans-serif" font-size="11" fill="#94a3b8">แปลงเป็นชื่อโฟลเดอร์</text>
  <text x="336" y="76" font-family="Consolas,monospace" font-size="12" fill="#94a3b8">E--Project-...-Claude</text>
  <text x="526" y="65" font-family="Segoe UI,sans-serif" font-size="14" font-weight="700" fill="#64748b">→</text>
  <rect x="560" y="30" width="180" height="60" rx="10" fill="#0f1626" stroke="#10b981" stroke-opacity="0.5"/>
  <text x="576" y="54" font-family="Segoe UI,sans-serif" font-size="13" font-weight="700" fill="#4ade80">🧠 memory เดิม</text>
  <text x="576" y="76" font-family="Segoe UI,sans-serif" font-size="11" fill="#94a3b8">มีความจำครบ ✓</text>
  <line x1="20" y1="120" x2="740" y2="120" stroke="#1f2937" stroke-dasharray="4 4"/>
  <text x="20" y="112" font-family="Segoe UI,sans-serif" font-size="11" fill="#94a3b8">เมื่อสร้างโฟลเดอร์ใหม่ ↓</text>
  <rect x="20" y="150" width="240" height="60" rx="10" fill="#0f1626" stroke="#f59e0b" stroke-opacity="0.5"/>
  <text x="36" y="174" font-family="Segoe UI,sans-serif" font-size="13" font-weight="700" fill="#fbbf24">path โปรเจกต์ใหม่</text>
  <text x="36" y="196" font-family="Consolas,monospace" font-size="12" fill="#64748b">...My-New-Project/</text>
  <text x="286" y="185" font-family="Segoe UI,sans-serif" font-size="14" font-weight="700" fill="#64748b">→</text>
  <rect x="320" y="150" width="180" height="60" rx="10" fill="#111827" stroke="#1f2937"/>
  <text x="336" y="174" font-family="Segoe UI,sans-serif" font-size="11" fill="#94a3b8">ชื่อโฟลเดอร์ "ใหม่"</text>
  <text x="336" y="196" font-family="Consolas,monospace" font-size="12" fill="#94a3b8">E--My-New-Project</text>
  <text x="526" y="185" font-family="Segoe UI,sans-serif" font-size="14" font-weight="700" fill="#64748b">→</text>
  <rect x="560" y="150" width="180" height="60" rx="10" fill="#0f1626" stroke="#ef4444" stroke-opacity="0.5"/>
  <text x="576" y="174" font-family="Segoe UI,sans-serif" font-size="13" font-weight="700" fill="#fca5a5">🧠 memory ใหม่</text>
  <text x="576" y="196" font-family="Segoe UI,sans-serif" font-size="11" fill="#94a3b8">ว่างเปล่า — เริ่มจาก 0</text>
  <text x="20" y="250" font-family="Segoe UI,sans-serif" font-size="11" fill="#94a3b8">💡 path เปลี่ยน → ชื่อโฟลเดอร์ memory เปลี่ยน → Claude Code เปิดสมุดเล่มใหม่ที่ยังว่าง</text>
  <text x="20" y="272" font-family="Segoe UI,sans-serif" font-size="11" fill="#94a3b8">     นี่คือเหตุผลว่าทำไม "ก๊อปทุกอย่างแล้ว แต่หนูดียังจำอะไรไม่ได้"</text>
</svg>'''

CONTENT = f'''<p>หลายครั้งเวลาเราเริ่มงานชิ้นใหม่ เราอยากแยกมันออกมาเป็นโฟลเดอร์ของตัวเอง ไม่ปนกับงานเก่า แต่พอแยกออกมาแล้ว หนูดีกับทีม Agent ก็หายไปด้วย เพราะ Claude Code มองว่า "โฟลเดอร์ใหม่ = โปรเจกต์ใหม่ = ไม่รู้จักทีมนี้"</p>

<div class="analogy">
  <div class="emoji">📦</div>
  <p>ลองคิดว่าทีม Agent เหมือน <b>ทีมงานที่กำลังจะย้ายออฟฟิศ</b> — เราไม่ได้ย้ายแค่ "ตัวคน" แต่ต้องขน <b>คู่มือการทำงาน</b> (ความสามารถ) และ <b>แฟ้มความทรงจำ</b> (สิ่งที่ทีมเคยเรียนรู้) ไปด้วย ถ้าลืมขนอย่างใดอย่างหนึ่ง ทีมก็ทำงานได้ไม่เต็มที่</p>
</div>

<h2>ทีมงานอยู่ตรงไหนกันแน่?</h2>
<p>สิ่งที่ทำให้หนูดี "เป็นหนูดี" และทำให้ Agent ทั้ง 25 ตัวมีตัวตน จริง ๆ แล้วเก็บอยู่แค่ <strong>2 ที่</strong> เท่านั้น และน่าแปลกใจที่ <strong>หนึ่งในนั้นอยู่นอกโฟลเดอร์โปรเจกต์</strong></p>

<figure>{SVG_WHERE}
<figcaption>ภาพรวม: <code>.claude/</code> และ <code>CLAUDE.md</code> อยู่ในโปรเจกต์ — แต่ <code>memory/</code> อยู่ข้างนอก แล้วผูกกลับด้วย "ชื่อ path"</figcaption>
</figure>

<h3>แปลเป็นภาษาคน</h3>
<ul>
  <li><strong>.claude/agents/</strong> — คือ "ตัวคน" ทั้ง 25 Agent แต่ละไฟล์คือสมองของ Agent หนึ่งตัว</li>
  <li><strong>.claude/skills/</strong> — คือ "ทักษะ" ที่หยิบมาใช้ซ้ำได้ เช่น ทำไดอะแกรม เขียน blog</li>
  <li><strong>settings.json + startup_hook.py</strong> — กฎและพิธีเปิดงาน เช่น สั่งให้อ่าน memory ก่อนเริ่มทุกครั้ง</li>
  <li><strong>CLAUDE.md</strong> — คู่มือเล่มใหญ่ บอกว่าใครทำอะไร และเวลามีงานเข้าให้ส่งต่อให้ใคร</li>
  <li><strong>memory/</strong> — สมุดบันทึกความทรงจำ ที่หนูดีจดสิ่งที่เรียนรู้ไว้ข้ามวันข้ามครั้ง</li>
</ul>

<h2>กับดักเรื่องความจำ (จุดที่คนพลาดบ่อยที่สุด)</h2>
<p>นี่คือหัวใจของคู่มือทั้งหน้านี้ Claude Code <strong>ไม่ได้</strong>เก็บโฟลเดอร์ <code>memory/</code> ไว้ในโปรเจกต์ แต่เก็บไว้ที่ส่วนกลางของเครื่อง แล้ว <strong>ตั้งชื่อโฟลเดอร์ตาม path ของโปรเจกต์</strong></p>

<figure>{SVG_MEMORY}
<figcaption>กลไก: path ของโปรเจกต์ถูกแปลงเป็นชื่อโฟลเดอร์ memory — พอ path เปลี่ยน Claude Code ก็เปิด "สมุดเล่มใหม่" ที่ยังว่าง</figcaption>
</figure>

<div class="callout c-tip">
  <span class="ico">💡</span>
  <p><span class="ttl">ข่าวดีสำหรับ "ทีมสะอาด"</span>ถ้าเราตั้งใจจะ <strong>เริ่มใหม่จากศูนย์</strong> อยู่แล้ว กับดักนี้กลายเป็น <strong>ของแถม</strong> ทันที เพราะ Claude Code จะสร้างโฟลเดอร์ memory ว่าง ๆ ให้เราเอง เราจึง <strong>ไม่ต้องก๊อป memory/</strong> เลย</p>
</div>

<h2>ลงมือทำ — เริ่มทีมใหม่สะอาด ๆ</h2>

<div class="step">
  <div class="step__n">1</div>
  <div class="step__body">
    <h3>ก๊อป .claude/ ไปทั้งโฟลเดอร์</h3>
    <p>นี่คือ "สมองและทักษะ" ของทีมทั้งหมด ก๊อปยกโฟลเดอร์ไปวางในโปรเจกต์ใหม่ได้เลย</p>
    <pre><code>cp -r .claude/ "path/ไปยัง/My-New-Project/"</code></pre>
  </div>
</div>

<div class="step">
  <div class="step__n">2</div>
  <div class="step__body">
    <h3>ก๊อป CLAUDE.md ไปด้วย</h3>
    <p>คู่มือ routing ของทีม — แต่เดี๋ยวต้องแก้เนื้อหา เพราะตอนนี้เต็มไปด้วยเรื่องธุรกิจเดิม</p>
  </div>
</div>

<div class="step">
  <div class="step__n">3</div>
  <div class="step__body">
    <h3>เลือก skill ที่จำเป็น (ไม่ต้องเอาทั้ง 12)</h3>
    <p>skill บางตัวผูกกับระบบ Django blog เดิม ถ้างานใหม่ไม่เกี่ยวก็ลบทิ้งได้</p>
  </div>
</div>

<div class="step">
  <div class="step__n">4</div>
  <div class="step__body">
    <h3>เปิด Claude Code ในโฟลเดอร์ใหม่ — จบ!</h3>
    <p>Claude Code จะสร้างโฟลเดอร์ <code>memory/</code> ว่าง ๆ ให้เองอัตโนมัติ ได้ทีมสะอาดพร้อมเริ่มงานทันที</p>
  </div>
</div>

<div class="callout c-warn">
  <span class="ico">🚫</span>
  <p><span class="ttl">ไม่ต้องก๊อป 2 อย่างนี้</span><code>settings.local.json</code> (permission สะสมของเครื่องเดิม ปล่อยให้สร้างใหม่ดีกว่า) และ <code>memory/</code> (ปล่อยให้เริ่มว่าง ๆ)</p>
</div>

<h2>3 จุดที่ "ต้องแก้" หลังก๊อป</h2>
<p>ไม่แก้แล้วทีมจะทำงานเพี้ยน เพราะยังชี้กลับไปของเดิม</p>

<h3>① startup_hook.py — path ฝังตายตัว</h3>
<p>ไฟล์นี้มี path เต็ม ๆ ชี้กลับไป memory ของโปรเจกต์เดิม ต้องเปลี่ยนให้ตรงโปรเจกต์ใหม่ หรือลบ hook นี้ทิ้งไปก่อนได้</p>

<h3>② CLAUDE.md — ลบเรื่องธุรกิจเดิมออก</h3>
<p>เก็บไว้แค่โครงที่ใช้ซ้ำได้ (ตาราง 25 Agents, วิธี activate, routing) แล้วเขียนส่วนที่เหลือใหม่ให้ตรงงานใหม่</p>

<h3>③ settings.json — เคลียร์ path เฉพาะเครื่อง</h3>
<p>มี <code>additionalDirectories</code> ที่ชี้ไป static ของโปรเจกต์เดิม ลบออกหรือแก้ให้ตรงโปรเจกต์ใหม่</p>

<div class="callout c-danger">
  <span class="ico">⚠️</span>
  <p><span class="ttl">skill 4 ตัวนี้ผูกกับ Django</span>ถ้าโปรเจกต์ใหม่ไม่มีระบบ blog พวกนี้จะใช้ไม่ได้: <code>django-blog-publisher</code>, <code>diagram-to-blog</code> และ skill ที่อ้าง Calendar API <code>localhost:8000</code> — ถ้างานใหม่ไม่เกี่ยวกับ blog แนะนำไม่ต้องก๊อป skill กลุ่มนี้</p>
</div>

<h2>สรุป &amp; Checklist</h2>
<div class="checklist">
  <ul>
    <li>ก๊อป <code>.claude/</code> (agents + skills + settings.json + startup_hook.py)</li>
    <li>ก๊อป <code>CLAUDE.md</code></li>
    <li>เลือก skill เท่าที่จำเป็น ลบตัวที่ผูกกับ Django ถ้าไม่ใช้</li>
    <li>แก้ path ใน <code>startup_hook.py</code> (หรือลบ hook ทิ้ง)</li>
    <li>เขียน <code>CLAUDE.md</code> ใหม่ให้ตรงงานใหม่ เก็บแค่โครงทีม</li>
    <li>ลบ <code>additionalDirectories</code> เก่าใน <code>settings.json</code></li>
    <li><strong>อย่า</strong>ก๊อป <code>memory/</code> และ <code>settings.local.json</code> — ปล่อยให้สร้างใหม่</li>
  </ul>
</div>
'''

obj, created = Article.objects.update_or_create(
    slug="team-new-project-guide",
    defaults=dict(
        title="ย้ายทีมหนูดีไปทำงานโปรเจกต์ใหม่ ต้องขนอะไรไปบ้าง?",
        author=author,
        category=category,
        excerpt="สร้างโฟลเดอร์ใหม่แล้วอยากให้หนูดีกับทีม Agent ตามไปทำงาน — คู่มือนี้พาดูว่าตัวตนของทีมอยู่ตรงไหน ก๊อปอะไร และกับดักเรื่องความจำที่คนมักพลาด",
        meta_description="คู่มือย้ายทีม AI Agent ไปโปรเจกต์ใหม่ใน Claude Code — ก๊อป .claude/ + CLAUDE.md และเข้าใจว่าทำไม memory ถึงหาย",
        content=CONTENT,
        layout="docs",
        status="draft",
    ),
)

print(("สร้างใหม่" if created else "อัปเดต") + f" Article #{obj.pk} | slug={obj.slug} | layout={obj.layout} | status={obj.status}")
print(f"author={author.username} | category={category.name}")
print(f"URL (เมื่อรัน server): /blog/{obj.slug}/")
