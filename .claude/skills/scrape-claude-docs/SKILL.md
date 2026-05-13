---
name: scrape-claude-docs
description: Scrape and structure documentation from code.claude.com/docs into clean markdown for Thai content creation. Use when Content Writer needs source material from official Claude Code documentation.
---

# Skill: Scrape Claude Docs

ดึงเนื้อหาจาก https://code.claude.com/docs/ มาแปลงเป็น structured markdown
สำหรับใช้เป็นแหล่งข้อมูลในการเขียนบทความภาษาไทย

## เมื่อไหร่ใช้
- Content Writer (TH) ต้องเขียนบทความเรื่อง Claude Code
- ต้องการ source material อย่างเป็นทางการ ไม่ใช่ข้อมูลมั่ว
- ต้องการ track เวลา docs มีการอัพเดท

## ขั้นตอน

### Step 1: Inventory หน้าใน docs
ใช้ WebFetch ดึง sitemap หรือ index page ของ https://code.claude.com/docs/
list หน้าทั้งหมด พร้อม URL + title

### Step 2: ดึงเนื้อหารายหน้า
สำหรับแต่ละหน้า:
```
WebFetch(url=<page>, prompt="Extract the main documentation content as clean markdown.
Preserve: headings (H1-H4), code blocks with language tags, bullet lists, tables,
inline links. Strip: navigation, footer, sidebar. Return only the article body.")
```

### Step 3: บันทึกเป็นไฟล์
โครงสร้างไฟล์:
```
docs/claude-code-source/
  ├── INDEX.md              # รายการหน้าทั้งหมด + last_scraped date
  ├── getting-started.md
  ├── slash-commands.md
  ├── hooks.md
  ├── mcp-servers.md
  └── ...
```

แต่ละไฟล์มี frontmatter:
```yaml
---
source_url: https://code.claude.com/docs/...
scraped_at: 2026-05-09
title: <original title>
---
```

### Step 4: สร้าง Topic Map สำหรับ Content Writer
สร้าง `docs/claude-code-source/TOPIC_MAP.md` แมปหัวข้อ → ไฟล์ source
เพื่อให้ Content Writer หาข้อมูลได้เร็ว เช่น:

| หัวข้อบทความไทย | Source files |
|----------------|--------------|
| Claude Code คืออะไร เริ่มยังไง | getting-started.md, installation.md |
| สอนเขียน Slash Command | slash-commands.md |
| ใช้ Hooks ทำ automation | hooks.md, settings.md |

## Output ที่ส่งกลับ
- Path ไปยัง `docs/claude-code-source/`
- จำนวนหน้าที่ scrape สำเร็จ / fail
- TOPIC_MAP.md updated

## หมายเหตุ
- รัน skill นี้ทุกเดือน (หรือเมื่อมี Claude Code update ใหญ่)
- ห้าม publish เนื้อหา scrape ดิบๆ — ต้อง rewrite เป็นไทยผ่าน Content Writer ก่อน (ไม่ใช่ translate)
- ถ้า WebFetch โดน rate limit → ทำ batch ละ 5 หน้า เว้น 30 วินาที
