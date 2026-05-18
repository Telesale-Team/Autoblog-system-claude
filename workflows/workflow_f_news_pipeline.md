# Workflow F: AI News Pipeline

**Trigger:** Manual ("Activate AI News Scout - ดึงข่าววันนี้") หรือ Scheduled (daily)
**Owner:** `ai-news-scout`
**SLA:** brief พร้อมภายใน 10 นาที / บทความ draft พร้อมภายใน 2 ชั่วโมง

---

## ภาพรวม

```
[Trigger]
    ↓
[AI News Scout] — scrape-ai-news skill
    ↓ brief (JSON, relevance ≥ 6)
[Content Writer TH] — เขียนบทความภาษาไทย
    ↓ draft article
[QA Agent] — ตรวจคุณภาพ
    ↓ approved
[django-blog-publisher] — โพสเป็น status="draft"
    ↓
[ผู้ใช้] — กด publish ใน Django Admin เอง
    ↓
[Data Analyst] — track traffic / performance (weekly)
```

---

## Step-by-Step

### Step 1 — Scout (AI News Scout)
- รัน skill `scrape-ai-news` กับ sources: Anthropic, OpenAI, Google DeepMind, Meta AI, xAI, Mistral
- Filter: relevance_score ≥ 6, max 5 ข่าว, diversity ≥ 3 ค่าย
- Output: structured brief array พร้อม `suggested_angle_th`
- เวลา: ≤ 10 นาที

### Step 2 — Select & Brief (AI News Scout)
- เลือก 1-2 ข่าวที่ score สูงสุดและ angle ชัดที่สุด
- ส่ง brief ให้ Content Writer TH พร้อมระบุ: ข่าวไหนก่อน/หลัง, tone ที่ต้องการ

### Step 3 — Write (Content Writer TH)
- รับ brief → เขียนบทความภาษาไทย format ข่าว (ไม่ใช่ long-form blog)
- ความยาว: 400-800 คำ
- โครงสร้าง: Lead (ใจความหลัก) → ความสำคัญต่อ SME ไทย → รายละเอียด → สรุป/CTA
- ใส่ meta: title_seo, meta_description, tags
- ห้าม: แปลตรงๆ, ใช้ศัพท์เทคนิคเกินไป

### Step 4 — QA (QA Agent)
- ตรวจ: ข้อเท็จจริงถูกต้องไหม, ภาษาไทยเป็นธรรมชาติไหม, SEO meta ครบไหม
- ถ้าผ่าน → ส่งต่อ Step 5
- ถ้าไม่ผ่าน → ส่งกลับ Content Writer TH พร้อม feedback

### Step 5 — Publish as Draft (django-blog-publisher)
- โพสบทความเข้า Django blog ด้วย `status="draft"` เสมอ
- ระบุ `category="ข่าว AI"` หรือสร้าง category ใหม่ถ้าไม่มี
- แนบ source URL ใน `excerpt` หรือ custom field

### Step 6 — Human Approval (ผู้ใช้)
- ผู้ใช้เข้า Django Admin → ตรวจบทความ → กด Publish
- ถ้าต้องแก้ → แก้ใน Admin หรือส่งกลับ Content Writer TH

### Step 7 — Track (Data Analyst) — weekly
- ดู traffic, time-on-page, conversion จาก AI news articles
- รายงานทุกศุกร์: ข่าวไหน perform ดีสุด → ใช้ปรับ angle ของสัปดาห์ถัดไป

---

## Timing

| Step | เวลา (SLA) |
|------|-----------|
| Step 1-2: Scout | ≤ 10 นาที |
| Step 3: Write | ≤ 60 นาที |
| Step 4: QA | ≤ 15 นาที |
| Step 5: Publish draft | ≤ 5 นาที |
| **รวม (ถึง draft)** | **≤ 90 นาที** |

---

## Error Handling

| สถานการณ์ | การจัดการ |
|-----------|-----------|
| ไม่มีข่าวที่ relevance ≥ 6 | Scout รายงาน → ไม่บังคับเขียน → รอวันถัดไป |
| WebFetch ล้มเหลว | ใช้ search snippet แทน + note ใน brief |
| QA ไม่ผ่าน 2 รอบ | Escalate ไปที่ Chief of Staff |
| django-blog-publisher error | Scout แจ้งผู้ใช้ให้โพสด้วย Admin ตรงๆ |

---

## ความแตกต่างจาก Workflow E (Content Pipeline)

| | Workflow E | Workflow F |
|--|-----------|-----------|
| Source | BACKLOG.md (topic ที่วางแผนไว้) | ข่าว AI ล่าสุดวันนี้ |
| Trigger | Manual (หนูดี - process backlog) | Manual หรือ Scheduled daily |
| ความยาว | 1,500-3,000 คำ (long-form SEO) | 400-800 คำ (news format) |
| SEO intent | Informational / evergreen | Newsjacking / timely |
| Agent เริ่ม | Marketing Specialist / SEO | AI News Scout |
