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

### Step 2: Design standards (ต้องทำทุกรูป)
- Background: `#0F172A` (Navy dark)
- Accent: `#C9A84C` (Gold)
- Font: Sarabun หรือ system Thai font
- Canvas: `1200x630px` (cover) หรือ `800x500px` (diagram)
- Export: **WebP format** ไม่เกิน 200KB

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
