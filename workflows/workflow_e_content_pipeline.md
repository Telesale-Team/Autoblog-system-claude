# Workflow E: Content Pipeline (SEO-Driven Blog)

**Owner:** Marketing Specialist
**Goal:** เปลี่ยน organic search → lead generation
**Frequency:** วงจรต่อ 1 บทความ ใช้เวลา 3-5 วันทำการ

---

## Overview Flow

```
[Topic Idea] → SEO Research → Source → Outline → Draft
   → Cover Design → QA → On-page SEO → Publish → Track → Iterate
```

---

## Stages & SLAs

### Stage 1: Topic Selection (1 วัน)
**Owner:** Marketing Specialist
- เลือก topic จาก content calendar (อิง business goal เดือนนี้)
- ส่ง topic + business intent ให้ SEO Specialist
- **Output:** Topic brief (1 ย่อหน้า)

### Stage 2: Keyword Research (1 วัน)
**Owner:** SEO Specialist
**Skill:** `seo-keyword-research-th`
- วิจัย primary + secondary keywords
- วิเคราะห์ top 3 competitors
- กำหนด search intent + content angle
- **Output:** Keyword Brief ใน `content_briefs/<topic-slug>.md`

### Stage 3: Source Material (½ วัน — ถ้าเรื่อง Claude Code/AI tool)
**Owner:** AI Toolsmith
**Skill:** `scrape-claude-docs` (หรือเทียบเท่า)
- ดึง official docs / source ที่อ้างอิงได้
- **Output:** Reference materials ใน `docs/<topic>/`

### Stage 4: Outline (½ วัน)
**Owner:** Content Writer (TH)
- วาง H1 / H2 / H3 จาก Keyword Brief
- ส่ง SEO Specialist ตรวจ → approve
- **Output:** Outline approved

### Stage 5: Draft Writing (1-2 วัน)
**Owner:** Content Writer (TH)
- เขียน full draft ตาม Format A หรือ B
- ฝัง **infographic HTML 2-3 ตัว** ใน content (Pattern A: stat grid / Pattern B: steps)
- Self-edit checklist
- **Output:** Draft ใน `content_briefs/<topic-slug>-draft.md`

### Stage 6: Cover Image Design (½ วัน)
**Owner:** Frontend Designer
- ออกแบบ cover image ตาม Design System (Navy+Gold, Sarabun)
- ขนาด 1200×630px สำหรับ OG image + blog header
- ใส่ชื่อบทความ + branding logo
- ส่งไฟล์ให้ Content Writer ใส่ใน frontmatter
- **Output:** Cover image พร้อม path

### Stage 7: QA Review (½ วัน)
**Owner:** QA Agent
- ตรวจ: typo, grammar, factual accuracy, plagiarism
- ตรวจ tone & voice ตรง persona
- ส่ง feedback กลับ Content Writer (rev ≤ 2 รอบ)
- **Output:** QA approved

### Stage 8: On-Page SEO Audit (½ วัน)
**Owner:** SEO Specialist
- เช็ค on-page checklist 10 ข้อ
- ตรวจ schema markup
- เตรียม meta_title + meta_description
- **Output:** Final article ready to publish

### Stage 9: Publish (½ วัน)
**Owner:** AI Toolsmith
**Skill:** `django-blog-publisher`
- Publish ผ่าน Django admin หรือ skill
- Verify URL + meta tags
- Submit ไป Google Search Console
- **Output:** Live article + URL

### Stage 10: Track (ต่อเนื่อง)
**Owner:** Data Analyst + SEO Specialist
- Week 1: ตรวจ indexing
- Week 2-4: ตรวจ ranking, CTR, organic traffic
- Month 3: ประเมิน success → keep/update/sunset
- **Output:** Performance report

---

## Approval Matrix

| Decision | Owner | Approver |
|----------|-------|----------|
| Topic selection | Marketing | ตัวเอง (ถ้าใน calendar) |
| New topic cluster | Marketing | CEO |
| Publish article | Content Writer | SEO + QA |
| Featured on homepage | Marketing | CEO |
| Sunset (delete) article | SEO | Marketing |

---

## KPIs ของ Workflow

| KPI | Target |
|-----|--------|
| Articles published / month | TBD ตาม Marketing capacity |
| Time from topic → publish | ≤ 5 วันทำการ |
| Articles ranking top 10 in 3 months | ≥ 30% |
| Organic traffic / article (M3) | ≥ 100 visits/เดือน |
| Lead conversion rate | ≥ 2% |

---

## Failure Recovery

| Problem | Action |
|---------|--------|
| QA reject 3 รอบ | Marketing เข้ามา re-brief Content Writer |
| ไม่ติดอันดับใน 3 เดือน | SEO ทำ content audit + update / republish |
| Lead conversion ต่ำ | Marketing ทบทวน CTA + landing page |
| Source content outdated | AI Toolsmith re-run scraper, Content Writer update |
