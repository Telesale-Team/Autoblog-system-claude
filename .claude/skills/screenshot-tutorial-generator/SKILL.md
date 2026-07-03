---
name: screenshot-tutorial-generator
description: Capture real browser screenshots at each step of a tutorial (e.g. "สมัคร Gmail", "ตั้งค่า Facebook Page") using Playwright, then annotate each screenshot with step numbers, arrows, and button highlights using Pillow. Use when Graphic Designer needs to create a step-by-step visual guide with real UI screenshots instead of abstract diagrams.
---

# Skill: Screenshot Tutorial Generator

ถ่ายภาพหน้าจอ browser จริงทีละ step แล้วใส่ annotation (step number, ลูกศร, highlight ปุ่ม) ด้วย Pillow
ใช้สำหรับบทความ "วิธีสมัคร/ตั้งค่า/ใช้งาน [service]" ที่ต้องการภาพ UI จริง

## เมื่อไหร่ใช้
- บทความ how-to / tutorial ที่อธิบายการใช้งาน web app
- ต้องการภาพ screenshot จริงแทน diagram วาดมือ
- ต้องการ step-by-step visual guide

## Prerequisites
- Playwright ติดตั้งใน venv (`pip install playwright` + `playwright install chromium`)
- Python venv: `E:\Project Peyo Peyo\Agent Skill Claude\venv\Scripts\python.exe`
- รัน script ด้วย **PowerShell tool เท่านั้น**

## Input ที่ต้องการ

```yaml
tutorial_title: "วิธีสมัคร Gmail"
keyword_slug: "สมัคร-gmail"
output_dir: "scripts/article_assets/"
steps:
  - step: 1
    url: "https://accounts.google.com/signup"
    description: "เปิดหน้าสมัคร Gmail"
    highlight:    # element ที่ต้องการ highlight (CSS selector)
      - "input[name='firstName']"
    arrow_to: "input[name='firstName']"   # ลูกศรชี้ไปที่ element นี้
    wait_ms: 2000

  - step: 2
    url: null   # null = อยู่หน้าเดิม
    action: "click"
    selector: "button[type='submit']"
    description: "กดปุ่ม ถัดไป"
    highlight:
      - "button[type='submit']"
    arrow_to: "button[type='submit']"
    wait_ms: 1500
```

## ขั้นตอน

### Step 1: สร้าง Playwright script

```python
import asyncio
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
import os, io, sys

sys.path.insert(0, r'E:\Project Peyo Peyo\Agent Skill Claude')
OUTPUT_DIR = r'E:\Project Peyo Peyo\Agent Skill Claude\scripts\article_assets'

async def capture_steps(steps, keyword_slug):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})

        for s in steps:
            # navigate ถ้ามี URL
            if s.get('url'):
                await page.goto(s['url'])
                await page.wait_for_timeout(s.get('wait_ms', 1500))

            # action (click, fill)
            if s.get('action') == 'click' and s.get('selector'):
                await page.click(s['selector'])
                await page.wait_for_timeout(s.get('wait_ms', 1000))

            # แคปหน้าจอ
            screenshot_bytes = await page.screenshot(full_page=False)
            img = Image.open(io.BytesIO(screenshot_bytes))

            # annotate
            img = annotate_screenshot(img, s)

            # save WebP
            filename = f"{keyword_slug}-step{s['step']:02d}.webp"
            img.save(os.path.join(OUTPUT_DIR, filename), 'WEBP', quality=85)
            print(f"✅ Step {s['step']}: {filename}")

        await browser.close()
```

### Step 2: Annotation function (Pillow)

```python
def annotate_screenshot(img, step_info):
    draw = ImageDraw.Draw(img)
    W, H = img.size

    # === Step number badge (มุมซ้ายบน) ===
    badge_size = 52
    draw.ellipse([16, 16, 16+badge_size, 16+badge_size],
                 fill='#C9A84C')
    draw.text((16 + badge_size//2, 16 + badge_size//2),
              str(step_info['step']),
              fill='#0F172A', anchor='mm',
              font=get_font(28, bold=True))

    # === Description bar (ล่างสุด) ===
    bar_h = 56
    draw.rectangle([0, H-bar_h, W, H], fill='#0F172A')
    draw.text((W//2, H - bar_h//2),
              step_info['description'],
              fill='#FFFFFF', anchor='mm',
              font=get_font(18))

    # === Highlight box (ถ้ามี element) ===
    # ใช้ bounding box จาก Playwright ก่อน annotate
    if step_info.get('highlight_bbox'):
        for bbox in step_info['highlight_bbox']:
            x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']
            pad = 6
            draw.rectangle([x-pad, y-pad, x+w+pad, y+h+pad],
                           outline='#C9A84C', width=3)

    # === Arrow (ถ้ามี target) ===
    if step_info.get('arrow_pos'):
        ax, ay = step_info['arrow_pos']
        # วาดลูกศรชี้ไปที่ target
        draw.polygon([(ax, ay), (ax-20, ay-35), (ax+20, ay-35)],
                     fill='#C9A84C')

    return img
```

### Step 3: Blur sensitive info (optional)

```python
from PIL import ImageFilter

def blur_region(img, bbox):
    region = img.crop(bbox)
    blurred = region.filter(ImageFilter.GaussianBlur(radius=15))
    img.paste(blurred, bbox)
    return img
```

### Step 4: File naming (SEO)

```
[keyword-slug]-step01.webp
[keyword-slug]-step02.webp
...
```

### Step 5: สร้าง Image Brief

```markdown
| Step | File | Alt Text |
|------|------|---------|
| 1 | สมัคร-gmail-step01.webp | วิธีสมัคร gmail ขั้นตอนที่ 1 — กรอกชื่อ |
| 2 | สมัคร-gmail-step02.webp | วิธีสมัคร gmail ขั้นตอนที่ 2 — กดถัดไป |
```

### Step 6: เปิดรูปทั้งหมดให้ดู
```powershell
Get-ChildItem "scripts\article_assets\[keyword-slug]-step*.webp" | ForEach-Object { Start-Process $_.FullName }
```

## Output

```
scripts/article_assets/
├── สมัคร-gmail-step01.webp    (screenshot + annotation)
├── สมัคร-gmail-step02.webp
├── ...
└── image_brief_สมัคร-gmail.md
```

## Annotation Standards

| Element | Style |
|---------|-------|
| Step badge | Gold circle (#C9A84C), เลขขาว, มุมซ้ายบน |
| Description bar | Navy bar (#0F172A) ล่างสุด, ข้อความขาว |
| Highlight box | Gold border 3px รอบ element ที่ต้องกด |
| Arrow | Gold triangle ชี้ลงหา element |
| Blur zone | Gaussian blur radius 15 สำหรับ email/password |
| Brand tag | "Noodee BootBiz" มุมขวาล่าง เล็กๆ |

## Anti-pattern
- ❌ ถ่ายหน้าจอโดยไม่ใส่ step number — ผู้อ่านงงลำดับ
- ❌ ไม่ blur password/email field — privacy issue
- ❌ Export PNG — ต้องเป็น WebP
- ❌ ลืมเปิดรูปให้ดูหลังเสร็จ
- ❌ ใช้ Bash tool — ต้องใช้ PowerShell เท่านั้น
- ❌ headless=False บน server — ต้อง headless=True เสมอ
