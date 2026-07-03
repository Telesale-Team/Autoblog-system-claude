---
name: visual-qa-checklist
description: Auto-check visual content (diagrams, infographics, banners, cover images) for Navy+Gold color compliance, Thai text presence, file size, resolution, WebP format, SEO filename, and alt text before delivery. Use when Graphic Designer finishes any visual asset and needs QA sign-off before passing to Content Writer or publishing.
---

# Skill: Visual QA Checklist

ตรวจ visual content อัตโนมัติก่อน deliver — ครอบคลุม brand compliance, SEO, technical specs

## เมื่อไหร่ใช้
- Graphic Designer เสร็จงานทุกชิ้นก่อนส่ง Content Writer
- ก่อน inject diagram เข้าบทความ
- ก่อน upload banner ขึ้น social media
- เพื่อลด revision round

## Input ที่ต้องการ

```yaml
files:
  - path: "scripts/article_assets/ai-chatbot-sme-01-concept.webp"
    type: "diagram"          # diagram | infographic | cover | banner
    alt_text: "ai chatbot ธุรกิจ — diagram การทำงาน"
    expected_size: [800, 500]   # [width, height] px
  - path: "scripts/article_assets/ai-chatbot-sme-cover.webp"
    type: "cover"
    alt_text: "ai chatbot ธุรกิจ — คู่มือ SME ไทย"
    expected_size: [1200, 630]
```

## Checklist 15 ข้อ

### Technical (5 ข้อ)
- [ ] **Format** — ต้องเป็น `.webp` เท่านั้น (ไม่ใช่ jpg/png)
- [ ] **File size** — cover ≤ 150KB, diagram/infographic ≤ 200KB, banner ≤ 200KB
- [ ] **Resolution** — ตรงตาม expected_size ± 5%
- [ ] **Color mode** — RGB (ไม่ใช่ CMYK หรือ P)
- [ ] **Readable** — เปิด Pillow ได้ ไม่ corrupt

### Brand Compliance (4 ข้อ)
- [ ] **Navy dominant** — พื้นหลังใช้โทน `#0F172A` หรือ Navy family (hue 210-230, saturation > 40%)
- [ ] **Gold accent** — มีสี `#C9A84C` หรือ Gold family อยู่ในภาพ
- [ ] **Brand tag** — มีข้อความ "Noodee BootBiz" (cover + banner เท่านั้น)
- [ ] **No stripe** — ไม่มีเส้นแบ่งแนวนอนกลางภาพ (cover image rule)

### SEO (3 ข้อ)
- [ ] **Filename has keyword** — ชื่อไฟล์มีคำ keyword (ไม่ใช่ image001, diagram_v2 ฯลฯ)
- [ ] **Alt text provided** — alt_text ไม่ว่าง ความยาว ≥ 20 chars
- [ ] **Alt text has keyword** — alt_text มีคำ keyword อย่างน้อย 1 คำ

### Content (3 ข้อ)
- [ ] **Thai text present** — มีตัวอักษรไทยอย่างน้อย 1 จุด (สำหรับ diagram/infographic)
- [ ] **Not blank section** — รูปไม่มีพื้นที่ว่าง > 40% โดยไม่มี content
- [ ] **Readable contrast** — text บนพื้นหลังมี contrast เพียงพอ (คร่าวๆ)

## ขั้นตอน

### Step 1: สร้าง Python checker script

```python
from PIL import Image
import os, re

def check_visual(file_path, file_type, alt_text, expected_size):
    results = []
    img = Image.open(file_path)
    
    # Technical
    results.append(('Format WebP', file_path.endswith('.webp')))
    size_kb = os.path.getsize(file_path) / 1024
    max_kb = 150 if file_type == 'cover' else 200
    results.append((f'File size ≤ {max_kb}KB (actual: {size_kb:.0f}KB)', size_kb <= max_kb))
    results.append((f'Resolution {expected_size}', abs(img.width - expected_size[0]) <= expected_size[0]*0.05))
    
    # SEO
    filename = os.path.basename(file_path)
    has_keyword = not re.match(r'^(image|diagram|banner|cover|photo|img)\d*', filename)
    results.append(('Filename has keyword', has_keyword))
    results.append(('Alt text not empty', len(alt_text) >= 20))
    
    return results
```

### Step 2: Run checker + print report

```
=== Visual QA Report ===
File: ai-chatbot-sme-cover.webp

✅ Format WebP
✅ File size ≤ 150KB (actual: 98KB)
✅ Resolution 1200x630
✅ Filename has keyword
✅ Alt text not empty
⚠️ Alt text has keyword — ตรวจสอบ manual
✅ Brand tag present

Score: 13/15 — PASS (ต้องตรวจ 2 ข้อ manual)
```

### Step 3: สรุปผล
- **PASS** (≥ 13/15) → ส่ง Content Writer ได้
- **WARN** (10-12/15) → แจ้ง Graphic Designer แก้ก่อน
- **FAIL** (< 10/15) → ต้องทำใหม่

## Output

```
=== Visual QA Summary ===
✅ PASS: ai-chatbot-sme-01-concept.webp (15/15)
⚠️ WARN: ai-chatbot-sme-cover.webp (13/15) — ตรวจ alt text manual
❌ FAIL: banner-draft.png (8/15) — format ผิด, size เกิน, ไม่มี brand tag

Action required: แก้ไข 1 ไฟล์ก่อน deliver
```

## Anti-pattern
- ❌ ข้าม QA เพราะรีบ — ทุกไฟล์ต้องผ่าน checklist นี้ก่อนเสมอ
- ❌ PASS ไปทั้งหมดโดยไม่ตรวจ manual items — Thai text และ contrast ต้องดูด้วยตา
- ❌ แก้ไฟล์โดยไม่รัน QA ซ้ำ
