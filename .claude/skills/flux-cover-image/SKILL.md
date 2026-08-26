---
name: flux-cover-image
description: Generate blog cover images using HuggingFace FLUX API with Noodee character (nudee_A_nobg.png) + Pillow text overlay. Use when Graphic Designer needs to create a cover image for a blog article. One-shot workflow from topic to final WebP cover with Hook text, brand tag "Noodee BootBiz", and Navy+Gold design system.
---

# Skill: FLUX Cover Image Generator

Generate cover image บทความด้วย HuggingFace FLUX + น้องหนูดี + Pillow text overlay
One-shot จาก topic → ได้ cover WebP พร้อม publish

## เมื่อไหร่ใช้
- Content Writer TH ขอ cover image สำหรับบทความใหม่
- ต้องการ cover ที่มีน้องหนูดี + hook text ครบตาม Article Workflow
- ต้องการ cover ขนาด 1200x630px พร้อม SEO filename

## Prerequisites
- `HUGGINGFACE_API_KEY` ใน `.env` (มีอยู่แล้ว)
- `nudee_A_nobg.png` — path จาก project_huggingface memory
- Python venv มี Pillow + requests
- รู้ primary keyword + hook 3 บรรทัด ของบทความ

## Input ที่ต้องการ

```yaml
article_title: "ชื่อบทความภาษาไทย"
segment: "beauty_wellness"    # ⚠️ บังคับ — pose กับ mood มาจากตรงนี้ ไม่ต้องเลือกเอง
primary_keyword: "ai chatbot ธุรกิจ"
keyword_slug: "ai-chatbot-sme"
hook:
  line1: "ธุรกิจคุณยังตอบช้าอยู่ไหม?"
  line2: "AI Chatbot ตอบแทนได้ 24 ชั่วโมง"
  line3: "ไม่ต้องจ้างพนักงานเพิ่ม"
```

> `pose_category` กับ `background_mood` **เลิกรับเป็น input แล้ว** — ดึงจาก segment แทน
> เดิมคนเรียกเลือกเอง ทำให้บทความกลุ่มเดียวกันได้ปกคนละอารมณ์ และไม่ตรงกับ diagram
> ถ้าจำเป็นต้องฝืนท่าเป็นกรณีพิเศษ ให้ระบุ `pose_override:` พร้อมเหตุผล แล้วแจ้งผู้ใช้ด้วย

## ขั้นตอน

### Step 1: อ่าน Nudee Character Spec
- อ่าน `memory/project_nudee_character_spec.md` ก่อนเสมอ
- อ่าน `memory/feedback_cover_pose_hook.md` — Pose ต้องเชื่อมกับ hook
- อ่าน `memory/feedback_cover_image_rules.md` — ห้ามมี stripe, ใช้ nudee_A_nobg.png, brand tag = "Noodee BootBiz"

### Step 1.5: ดึง pose และ mood จาก segment (ทำก่อนยิง FLUX เสมอ)

```python
import sys; sys.path.insert(0, "scripts")
from segment_profile import load_segment, cover_prompt, nudee_pose_prompt, BRAND_TAG

seg = load_segment(segment)              # เช่น "beauty_wellness"
bg_prompt = cover_prompt(seg, article_title)
pose_desc = nudee_pose_prompt(seg)       # ต่อท้าย prompt base ใน character spec
hook_style = seg["cover"]["hook_style"]  # ใช้ตรวจว่า hook ที่เขียนมาเข้าแนวกลุ่มนี้ไหม
```

**ยังต้องตรวจกฎ pose ↔ hook ด้วยตาอีกชั้น** — segment บอกท่าตั้งต้น แต่กฎเดิมยังอยู่:
ท่าต้องล้อกับ hook ที่เขียนจริง ถ้า hook เป็นคำเตือนแต่ segment ให้ท่า `happy`
ให้ทักผู้ใช้ก่อน อย่าปล่อยผ่าน (ดู `feedback_cover_pose_hook`)

### Step 2: Generate background ด้วย FLUX API
```python
import requests, os
from dotenv import load_dotenv
load_dotenv()

API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}

# ใช้ bg_prompt จาก Step 1.5 — อย่าประกอบ prompt เอง
# cover_prompt() ใส่ "no text, no characters, no logos" ให้แล้ว
# (ถ้าให้ FLUX วาดตัวหนังสือจะได้ตัวอักษรมั่ว และหนูดีจะผิดสเปก)
payload = {"inputs": bg_prompt}
```

### Step 3: Composite ด้วย Pillow
Layout มาตรฐาน (1200x630px):
```
┌─────────────────────────────────────┐
│  [Background 1200x630]              │
│                                     │
│  [หนูดี PNG]    [Hook Line 1]       │
│  ซ้ายล่าง       [Hook Line 2]       │
│                 [Hook Line 3]       │
│                                     │
│  [Brand tag: "Noodee BootBiz"]      │
└─────────────────────────────────────┘
```

Design tokens:
- Background overlay: `rgba(15, 23, 42, 0.6)` (Navy semi-transparent)
- Hook text color: `#FFFFFF` (ขาว) + shadow
- Brand tag: `#C9A84C` (Gold)
- Font: Sarabun Bold สำหรับ hook, Regular สำหรับ brand tag

### Step 4: SEO File Naming
```
[keyword-slug]-cover.webp
ตัวอย่าง: ai-chatbot-sme-cover.webp
```

### Step 5: Export + เปิดให้ดู
- Export WebP quality=90, ≤ 150KB
- `Start-Process` เปิดรูปทันที
- แสดง alt text แนะนำ: `[primary_keyword] — [article_title]`

## Output

```
scripts/article_assets/
└── [keyword-slug]-cover.webp

Alt text แนะนำ: "ai chatbot ธุรกิจ — คู่มือ AI Chatbot สำหรับ SME ไทย"
File size: ≤ 150KB
Dimensions: 1200x630px
```

## Anti-pattern
- ❌ ลืมอ่าน nudee character spec → หนูดีออกมาผิด
- ❌ มี stripe หรือ divider กลางภาพ
- ❌ Hook ไม่เชื่อมกับ pose (เช่น pose "thinking" แต่ hook "ยินดีต้อนรับ")
- ❌ **เลือก pose/mood เองโดยไม่ดู segment** — ทำให้ปกไม่ตรงกับ diagram ของบทความเดียวกัน
- ❌ **ไม่ระบุ `segment`** — ถ้าไม่รู้ว่าบทความอยู่กลุ่มไหน ให้ถามก่อน อย่าเดา
- ❌ ประกอบ prompt พื้นหลังเอง ทั้งที่ `cover_prompt()` ทำให้แล้ว
- ❌ Brand tag ไม่ใช่ "Noodee BootBiz"
- ❌ Export PNG แทน WebP
- ❌ ขนาดเกิน 150KB
