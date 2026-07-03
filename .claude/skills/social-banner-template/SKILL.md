---
name: social-banner-template
description: Generate social media banners for 3 platforms (Facebook 1200x630, Instagram 1080x1080, LINE 1040x1040) simultaneously using Python Pillow templates. Use when Graphic Designer needs to create banners for a blog article or campaign across all social channels at once. Reduces turnaround from 30 min to 10 min per banner set.
---

# Skill: Social Banner Template System

สร้าง banner 3 platform พร้อมกันในครั้งเดียว: Facebook + Instagram + LINE
ใช้ Python Pillow template system ที่ auto-resize content ตาม platform

## เมื่อไหร่ใช้
- ต้องการ banner โปรโมตบทความใหม่ใน 3 platform พร้อมกัน
- Marketing Specialist ขอ banner สำหรับ campaign
- ต้องการ visual ที่มี branding Noodee BootBiz สม่ำเสมอ

## Prerequisites
- Python venv มี Pillow
- มี headline + sub-text ของ banner แล้ว
- รู้ว่า banner ใช้สำหรับ content ประเภทไหน

## Platform Specs

| Platform | ขนาด | Safe Zone | Format |
|----------|------|-----------|--------|
| Facebook Page | 1200×630px | center 900×500px | WebP |
| Instagram Feed | 1080×1080px | center 900×900px | WebP |
| LINE Broadcast | 1040×1040px | center 860×860px | WebP |

## Input ที่ต้องการ

```yaml
campaign_slug: "ai-chatbot-launch"        # สำหรับ file naming
headline: "AI Chatbot ตอบแทนคุณได้"       # ตัวหนาหลัก
subtext: "ไม่ต้องจ้างพนักงานเพิ่ม"        # บรรทัดสอง
cta: "อ่านต่อที่ Noodee BootBiz"          # call to action
background_style: "tech"                  # tech | warm | clean | gradient
include_nudee: true                       # ใส่รูปหนูดีไหม
article_url: "https://..."               # optional QR/link
```

## Design Standards (ทุก platform)

```
Colors:
  background:  #0F172A (Navy dark) หรือ gradient Navy→#1E3A5F
  headline:    #FFFFFF (ขาว) + drop shadow
  subtext:     #E2E8F0 (ขาวอมเทา)
  cta:         #C9A84C (Gold) background + Navy text
  brand tag:   "Noodee BootBiz" Gold เล็กๆ มุมขวาล่าง

Typography:
  headline: Sarabun Bold 48-64px (scale per platform)
  subtext:  Sarabun Regular 28-36px
  cta:      Sarabun SemiBold 24px
```

## ขั้นตอน

### Step 1: สร้าง base template function
```python
from PIL import Image, ImageDraw, ImageFont
import os

def make_banner(width, height, headline, subtext, cta, bg_style, nudee_path=None):
    img = Image.new('RGB', (width, height), color='#0F172A')
    # วาด background, ใส่หนูดี, ใส่ text, ใส่ brand tag
    return img

platforms = {
    'facebook': (1200, 630),
    'instagram': (1080, 1080),
    'line': (1040, 1040),
}
```

### Step 2: Loop generate ทุก platform
```python
for platform, (w, h) in platforms.items():
    banner = make_banner(w, h, headline, subtext, cta, background_style)
    filename = f"{campaign_slug}-{platform}.webp"
    banner.save(f"scripts/article_assets/{filename}", 'WEBP', quality=90)
    print(f"✅ {platform}: {filename}")
```

### Step 3: File naming (SEO standard)
```
[campaign-slug]-facebook.webp
[campaign-slug]-instagram.webp
[campaign-slug]-line.webp
```

### Step 4: เปิดให้ดูทั้ง 3 รูป
```powershell
Start-Process "scripts/article_assets/[campaign-slug]-facebook.webp"
Start-Process "scripts/article_assets/[campaign-slug]-instagram.webp"
Start-Process "scripts/article_assets/[campaign-slug]-line.webp"
```

## Output

```
scripts/article_assets/
├── ai-chatbot-launch-facebook.webp   (1200×630)
├── ai-chatbot-launch-instagram.webp  (1080×1080)
└── ai-chatbot-launch-line.webp       (1040×1040)
```

แต่ละไฟล์ ≤ 200KB, WebP format, brand-consistent ทุกใบ

## Anti-pattern
- ❌ ทำ banner ทีละ platform — ใช้ loop ทำพร้อมกันเสมอ
- ❌ ขนาด text เท่ากันทุก platform — ต้อง scale ตามขนาด canvas
- ❌ Export PNG — ต้องเป็น WebP
- ❌ ไม่มี brand tag "Noodee BootBiz"
- ❌ ลืมเปิดรูปให้ดูหลัง generate
