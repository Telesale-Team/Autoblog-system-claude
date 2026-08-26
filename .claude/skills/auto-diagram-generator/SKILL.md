---
name: auto-diagram-generator
description: Auto-generate Python Pillow diagrams for every H2 section in a blog article. Use when Graphic Designer receives article outline from Content Writer TH and needs to create matching diagrams for each section automatically. Saves manual briefing time — one call generates all diagrams for the article.
---

# Skill: Auto Diagram Generator

รับ article outline (H2 structure) แล้ว generate diagram PNG ด้วย Python Pillow สำหรับทุก H2 section อัตโนมัติ

## เมื่อไหร่ใช้
- Content Writer TH ส่ง outline พร้อม H2 list มาให้
- ต้องการ diagram ประกอบบทความตาม Article Workflow (ทุก H2 ต้องมี ≥ 1 diagram)
- ต้องการลด turnaround จากการ brief ทีละ section

## Prerequisites
- Python venv มี Pillow ติดตั้งแล้ว (`venv\Scripts\python.exe`)
- รู้ primary keyword ของบทความ (สำหรับตั้งชื่อไฟล์)
- มี H2 list ของบทความ

## Input ที่ต้องการ

```yaml
article_title: "ชื่อบทความภาษาไทย"
segment: "beauty_wellness"                   # ⚠️ บังคับ — คุมสไตล์ทั้งชุด (ดูหัวข้อถัดไป)
primary_keyword: "ai chatbot ธุรกิจ"        # สำหรับ file naming
keyword_slug: "ai-chatbot-sme"               # EN slug สำหรับ filename
output_dir: "scripts/article_assets/"
h2_sections:
  - heading: "AI Chatbot คืออะไร"
    type: "concept"                           # concept | steps | comparison | stats
    key_points: ["รับ input", "ประมวลผล", "ตอบกลับ"]
  - heading: "ขั้นตอนติดตั้ง"
    type: "steps"
    key_points: ["สมัคร API", "ตั้งค่า", "ทดสอบ", "Deploy"]
  - heading: "เปรียบเทียบ AI Tools"
    type: "comparison"
    key_points: ["ChatGPT", "Claude", "Gemini"]
```

## สิ่งที่ skill ทำ

### Step 1: สร้าง Python script อัตโนมัติ
สร้าง `scripts/gen_diagrams_[keyword_slug].py` ที่:
- Loop ทุก H2 section
- เลือก diagram style ตาม `type`:
  - `concept` → flow diagram แนวนอน
  - `steps` → numbered step flow แนวตั้ง
  - `comparison` → comparison table/grid
  - `stats` → bar/metric cards

### Step 1.5: ดึงสไตล์ของ segment (ทำก่อนวาดเสมอ)

**ห้าม hardcode สไตล์เอง** — อ่านจาก `marketing.SegmentProfile` ผ่านตัวช่วยกลาง
ถ้าไม่รู้ว่าบทความนี้อยู่ segment ไหน ให้ถามก่อน อย่าเดา

```python
import sys; sys.path.insert(0, "scripts")
from segment_profile import load_segment, diagram_style

seg = load_segment(segment)          # เช่น "beauty_wellness"
style = diagram_style(seg)
# {'bg': '#0F172A', 'primary': '#C9A84C', 'accent': '#E8B4B8',
#  'corner_radius': 24, 'stroke_width': 2, 'prefer_type': 'steps'}
```

ดูค่าเร็ว ๆ จาก command line:
```
venv\Scripts\python.exe scripts/segment_profile.py --list
venv\Scripts\python.exe scripts/segment_profile.py beauty_wellness
```

**สิ่งที่ segment คุม:**

| ค่าจาก segment | เอาไปใช้ตรงไหน |
|---|---|
| `corner_radius` | ความโค้งมุมของทุกกล่องใน diagram (24 / 12 / 0) |
| `accent` | สีเน้นจุดเดียวต่อรูป — เส้นชี้ ตัวเลขลำดับ ไอคอนเดี่ยว |
| `stroke_width` | ความหนาเส้นไอคอนและกรอบ |
| `prefer_type` | ชนิด diagram ที่กลุ่มนี้ชอบ — ใช้เมื่อ H2 นั้นไม่ได้ระบุ `type` มา |

### Step 2: Design standards (ต้องทำทุกรูป)
- Background: `#0F172A` (Navy dark) — **ห้ามเปลี่ยนตาม segment**
- Primary: `#C9A84C` (Gold) — **ห้ามเปลี่ยนตาม segment**
- Accent: `style["accent"]` — สีรองของ segment **ใช้ได้จุดเดียวต่อรูป**
  ห้ามเอาไปเป็นพื้นหลัง สีหัวข้อ หรือสีกรอบทุกกล่อง ไม่งั้นจะแย่งสีแบรนด์
- Corner radius: `style["corner_radius"]` (มาจาก segment ไม่ใช่เลือกเอง)
- Font: Sarabun หรือ system Thai font
- Canvas: `1200x630px` (cover) หรือ `800x500px` (diagram)
- Export: **WebP format** ไม่เกิน 200KB

### Step 2.5: หยุดให้เจ้าของอนุมัติ prompt ก่อนสร้างรูปจริง (บังคับ)

**ห้ามยิงสร้างรูปก่อนได้รับอนุมัติ** — แก้ prompt ราคาศูนย์ แต่แก้รูปที่สร้างเสร็จแล้ว
ต้องเผาโควตาใหม่ทั้งชุด

ที่มาแนวคิด: HITL checkpoint ใน `AI-Content-Studio/agents.py` ซึ่งหยุดให้คนแก้
prompt ของทุกฉากก่อน generate จริง

แสดงตารางนี้ให้เจ้าของดูก่อนเสมอ:

```
กำลังจะสร้าง diagram N รูป สำหรับ "<ชื่อบทความ>" (segment: <key>)
สไตล์: มุมโค้ง <corner_radius> · เส้นหนา <stroke_width> · สีเน้น <accent>

| # | H2 | ชนิด | สิ่งที่จะวาด |
|---|----|------|-------------|
| 1 | ... | steps | กล่อง 4 ขั้น เรียงลงล่าง มีเลขลำดับสีทอง |
| 2 | ... | ...   | ... |

พิมพ์ "ok" เพื่อสร้าง หรือบอกว่าจะแก้รูปไหนอย่างไร
```

**ข้ามขั้นนี้ได้กรณีเดียว** — เจ้าของสั่งไว้ล่วงหน้าในข้อความเดียวกันว่าไม่ต้องถาม

### Step 3: File naming (SEO standard)
```
[keyword-slug]-[section-number]-[descriptor].webp
ตัวอย่าง: ai-chatbot-sme-01-concept.webp
          ai-chatbot-sme-02-steps.webp
          ai-chatbot-sme-03-comparison.webp
```

### Step 4: สร้าง Image Brief สำหรับ Content Writer
Output เป็น `image_brief_[keyword_slug].md`:
```markdown
## Image Brief — [article_title]

| Section | File | Alt Text | Caption |
|---------|------|---------|---------|
| H2: AI Chatbot คืออะไร | ai-chatbot-sme-01-concept.webp | ai chatbot ธุรกิจ — diagram แสดงการทำงานของ AI Chatbot | การทำงานของ AI Chatbot | Noodee BootBiz |
...
```

### Step 5: รัน script + เปิดรูปให้ดู
- รัน script ด้วย `venv\Scripts\python.exe`
- `Start-Process` เปิดรูปทุกใบให้ดูทันที

## Output

```
scripts/article_assets/
├── ai-chatbot-sme-01-concept.webp
├── ai-chatbot-sme-02-steps.webp
├── ai-chatbot-sme-03-comparison.webp
└── image_brief_ai-chatbot-sme.md
```

## Anti-pattern
- ❌ ตั้งชื่อไฟล์ไม่มี keyword slug
- ❌ Export เป็น JPG หรือ PNG (ต้องเป็น WebP)
- ❌ ขนาดไฟล์เกิน 200KB
- ❌ ไม่สร้าง image_brief.md — Content Writer จะไม่รู้ alt text
- ❌ **ไม่ระบุ `segment` หรือเดาเอง** — สไตล์ผิดกลุ่มมองไม่ออกจากรูป กว่าจะรู้ก็สายแล้ว
- ❌ **เอา `accent` ของ segment ไปใช้เป็นพื้นหลังหรือสีหัวข้อ** — มันคือสีรอง ใช้จุดเดียวต่อรูป
- ❌ **เปลี่ยนสีกรม/ทองตาม segment** — สองสีนี้คือแบรนด์ ห้ามแตะ
- ❌ hardcode `corner_radius` หรือความหนาเส้นเอง ทั้งที่ segment กำหนดไว้แล้ว

## ใบงานประจำบทความ (รันซ้ำแล้วไม่ทำซ้ำ)

ก่อนเริ่มให้เช็คว่าขั้นนี้ทำไปแล้วหรือยัง:
```
venv\Scripts\python.exe scripts/article_manifest.py status <slug>
```
ถ้าขั้นนี้ขึ้นว่า "เสร็จ" แล้ว **อย่าทำซ้ำ** ให้ถามเจ้าของก่อนว่าจะสร้างทับไหม

ทำเสร็จแล้วบันทึก:
```
venv\Scripts\python.exe scripts/article_manifest.py done <slug> <cover|diagram>
```
