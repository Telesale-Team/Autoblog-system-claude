---
name: diagram-to-blog
description: Upload diagram/infographic PNG/WebP to Django Media and inject img tag into the correct H2 section of a draft article. Use when Graphic Designer has finished a diagram and needs to attach it to the matching section in a blog article without going through another agent.
---

# Skill: Diagram to Blog Publisher

Upload รูป diagram/infographic เข้า Django `/media/` และ inject `<img>` tag เข้าไปในบทความ draft ที่ H2 section ที่ถูกต้อง

## เมื่อไหร่ใช้
- Graphic Designer สร้าง diagram เสร็จและต้องการฝังเข้าบทความ
- ต้องการ inject รูปหลาย section พร้อมกัน
- บทความเป็น status="draft" อยู่ใน DB แล้ว

## Prerequisites
- ไฟล์รูป WebP อยู่ใน `scripts/article_assets/`
- รู้ article slug หรือ article ID ใน Django DB
- มี image_brief.md ที่ระบุ alt text + caption ของแต่ละรูปไว้แล้ว
- Django server รันอยู่ที่ port 8000

## Input ที่ต้องการ

```yaml
article_id: 42                    # หรือ slug: "ai-chatbot-sme-guide"
diagrams:
  - file: "scripts/article_assets/ai-chatbot-sme-01-concept.webp"
    target_h2: "AI Chatbot คืออะไร"    # ใส่หลัง H2 นี้
    alt: "ai chatbot ธุรกิจ — diagram การทำงานของ AI Chatbot"
    caption: "การทำงานของ AI Chatbot | Noodee BootBiz"
  - file: "scripts/article_assets/ai-chatbot-sme-02-steps.webp"
    target_h2: "ขั้นตอนติดตั้ง"
    alt: "ขั้นตอนติดตั้ง ai chatbot — 4 steps diagram"
    caption: "4 ขั้นตอนติดตั้ง AI Chatbot | Noodee BootBiz"
```

## ขั้นตอน

### Step 1: Copy รูปเข้า Django media folder
```python
import shutil, os
media_path = r"E:\Project Peyo Peyo\Agent Skill Claude\media\blog"
shutil.copy(diagram_file, os.path.join(media_path, filename))
```

### Step 2: ดึง article content จาก DB
```python
import django, os, sys
sys.path.insert(0, r'E:\Project Peyo Peyo\Agent Skill Claude')
os.environ['DJANGO_SETTINGS_MODULE'] = 'AI_automate.settings'
django.setup()
from blog.models import Article
article = Article.objects.get(id=article_id)
content = article.content
```

### Step 3: Inject `<img>` tag หลัง H2 — REVERSE LOOP
**สำคัญ:** Insert หลายจุดต้อง reverse loop เสมอ (feedback_string_insert_order.md)

```python
# หา position ของ H2 target จาก ท้ายสุดก่อน
img_tag = f'<figure><img src="/media/blog/{filename}" alt="{alt}" loading="lazy"><figcaption>{caption}</figcaption></figure>'
h2_tag = f'<h2>{target_h2}</h2>'
insert_pos = content.find(h2_tag) + len(h2_tag)
content = content[:insert_pos] + img_tag + content[insert_pos:]
```

### Step 4: Save กลับ DB
```python
article.content = content
article.save()
print(f"Injected {filename} into '{target_h2}' section")
```

### Step 5: Verify
- เปิด `http://localhost:8000/admin/blog/article/{article_id}/change/` ให้ดู

## Output
- รูปอยู่ใน `/media/blog/[filename].webp`
- `<img>` tag ถูก inject เข้าบทความแต่ละ H2 section แล้ว
- Article status ยังเป็น `draft` (ไม่ publish อัตโนมัติ)

## Anti-pattern
- ❌ Forward loop ใส่รูปหลายจุด → position เลื่อน → ผิด section
- ❌ Publish article หลัง inject — ต้องเป็น draft เสมอ
- ❌ ใส่รูปโดยไม่มี alt text
- ❌ ลืม caption
