---
name: django-blog-publisher
description: Publish articles directly to the Django blog app (blog.models.Article) with full SEO metadata. Use when Content Writer has finalized content and SEO Specialist has approved on-page checklist.
---

# Skill: Django Blog Publisher

โพสบทความเข้า Django blog app ของเว็บเรา พร้อม SEO metadata ครบถ้วน
ใช้เมื่อบทความผ่าน Content Writer + SEO + QA แล้ว

## Prerequisites
- บทความผ่าน QA Agent แล้ว (ไม่มี typo, factual error)
- ผ่าน on-page SEO checklist จาก SEO Specialist
- มี cover image + og image พร้อม
- รู้ category + tags ที่จะใช้

## Input ที่ต้องการ (Article Spec)
```yaml
title: "หัวข้อภาษาไทย ≤ 200 chars"
slug: "english-kebab-case-with-keyword"  # optional, auto-gen ถ้าไม่ใส่
category: "ชื่อหมวด"  # ต้องมีอยู่แล้วใน DB
tags: ["tag1", "tag2", "tag3"]  # auto-create ถ้าไม่มี
excerpt: "สรุปย่อ ≤ 160 chars (ใช้เป็น meta desc fallback)"
content: |
  <p>เนื้อหา HTML format (CKEditor compatible)</p>
  <h2>หัวข้อย่อย</h2>
  ...
cover_image: "path/to/cover.jpg"  # relative to media/
og_image: "path/to/og.jpg"  # optional, ใช้ cover ถ้าไม่ใส่

# SEO
meta_title: "≤ 70 chars (override <title>)"
meta_description: "≤ 160 chars + CTA"

# Publish settings
status: "draft"   # ← ต้องเป็น draft เสมอ ผู้ใช้ publish เองใน Django admin
is_featured: false
author_username: "admin"  # หรือ user ที่จะเป็น author

# Backlog (optional แต่แนะนำ)
backlog_id: null  # ContentBacklog.pk ที่บทความนี้มาจาก (ถ้ามี)
```

## ขั้นตอนการ Publish

### Step 1: Validate input
- ตรวจ length: title ≤ 200, meta_title ≤ 70, meta_desc ≤ 160, excerpt ≤ 300
- ตรวจ category มีอยู่จริง (ถ้าไม่มี → ขออนุมัติสร้าง)
- ตรวจ author user มีอยู่
- ตรวจ image files มีอยู่จริงใน media/

### Step 2: รัน Django shell สร้าง Article + Link CalendarEvent

ใช้ PowerShell tool เสมอ (ไม่ใช่ Bash):
```powershell
$env:PYTHONIOENCODING = 'utf-8'
$script = @'
import sys; sys.stdout.reconfigure(encoding="utf-8")
from blog.models import Article, Category, Tag
from django.contrib.auth import get_user_model
User = get_user_model()

author = User.objects.get(username="<author_username>")
category = Category.objects.get(name="<category>")

article = Article.objects.create(
    title="<title>",
    slug="<slug>",
    author=author,
    category=category,
    excerpt="<excerpt>",
    content="<content_html>",
    meta_title="<meta_title>",
    meta_description="<meta_description>",
    cover_image="<cover_path>",
    og_image="<og_path>",
    status="draft",
    is_featured=False,
    backlog_ref_id=<backlog_id>,  # ใส่ None ถ้าไม่มาจาก backlog
)

for tag_name in [<tags>]:
    tag, _ = Tag.objects.get_or_create(name=tag_name)
    article.tags.add(tag)

# === Link CalendarEvent ผ่าน backlog chain ===
if article.backlog_ref_id:
    try:
        backlog = article.backlog_ref
        if backlog.calendar_event_id:
            from dashboard.models import CalendarEvent
            CalendarEvent.objects.filter(pk=backlog.calendar_event_id).update(
                article=article,
                title=article.title,
                description=f"Draft: {article.title}",
            )
            print(f"Linked CalendarEvent pk={backlog.calendar_event_id} to article pk={article.pk}")
    except Exception as e:
        print(f"Warning: could not link calendar event: {e}")

print(f"OK id={article.id} url={article.get_absolute_url()}")
'@
$script | .\venv\Scripts\python.exe manage.py shell
```

**กฎ:** `status` ต้องเป็น `"draft"` เสมอ — ผู้ใช้ publish เองใน Django admin

### Step 3: Verify หลัง publish
- ตรวจ URL: `<base>/blog/<slug>/` เปิดได้
- ตรวจ meta tags ใน source: `<title>`, `<meta name="description">`, og: tags
- Submit URL ไป Google Search Console (manual หรือ auto via Indexing API)

### Step 4: Log
บันทึกใน `content_briefs/<topic-slug>.md`:
```markdown
## Published
- **Date:** YYYY-MM-DD HH:MM
- **Article ID:** <id>
- **URL:** <full url>
- **GSC submitted:** yes/no
```

## Anti-pattern
- ❌ ห้าม publish โดยไม่ผ่าน QA
- ❌ ห้ามใช้ `status="published"` ถ้ายังขาด meta_description
- ❌ ห้ามตั้ง `is_featured=true` โดยไม่ขออนุมัติ Marketing Specialist
- ❌ ห้ามใช้ slug ภาษาไทย (Google ไม่ชอบ, อ่านยาก)

## Roll-back
ถ้า publish ผิด:
```python
Article.objects.get(id=<id>).delete()
# หรือถ้าต้องเก็บไว้ revise:
Article.objects.filter(id=<id>).update(status="draft")
```
