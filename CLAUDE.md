# AI Automation Business — 26-Agent System

ระบบ AI Agent สำหรับธุรกิจ AI Automation Specialist ที่ขายระบบ AI ให้ SME ไทย

**Version:** 2.9 | **Updated:** 2026-08-23

---

## 🔴 STARTUP PROTOCOL — ทำก่อนทุกอย่างเสมอ

**ทุก session ใหม่ ทำตามลำดับนี้:**

> ⚠️ **Memory ไม่ได้อยู่ในโฟลเดอร์โปรเจกต์** — อยู่ที่ absolute path นี้เท่านั้น:
> `C:\Users\dphoo\.claude\projects\E--Project-Peyo-Peyo-Agent-Skill-Claude\memory`
> (ใช้ path เต็มทุกครั้ง — path แบบ `memory/...` จะหาไม่เจอ โดยเฉพาะเมื่อเป็น subagent)

1. อ่าน `C:\Users\dphoo\.claude\projects\E--Project-Peyo-Peyo-Agent-Skill-Claude\memory\MEMORY.md` ทุกบรรทัด
2. อ่าน memory file ที่เกี่ยวข้องกับงานที่จะทำ
3. ดูงานค้างจาก Calendar API: `GET http://localhost:8000/owner/api/events/` และ Notes: `GET http://localhost:8000/owner/api/notes/`
4. ค่อยตอบหรือรับงาน

**ห้าม assume ว่าจำได้** — ต้อง verify จาก memory files จริงๆ ทุกครั้ง
โดยเฉพาะก่อนทำงานกับ server ต้องอ่าน `C:\Users\dphoo\.claude\projects\E--Project-Peyo-Peyo-Agent-Skill-Claude\memory\project_deploy_workflow.md` ก่อนเสมอ

**สำหรับ subagent ทุกตัว:** subagent เกิดใหม่แบบ context เปล่า ไม่ได้รับ SessionStart hook
ข้อมูล server ที่จำเป็นจึงสรุปไว้ในหัวข้อถัดไปของไฟล์นี้ (CLAUDE.md ถูกส่งให้ subagent ด้วย)

---

## 🖥️ SERVER & DEPLOY — อ่านก่อนแตะ server ทุกครั้ง (ทุก agent รวม subagent)

**รายละเอียดเต็ม:** `C:\Users\dphoo\.claude\projects\E--Project-Peyo-Peyo-Agent-Skill-Claude\memory\project_deploy_workflow.md`

### SSH
```
ssh -i ~/.ssh/id_ubuntu_local dphoompat@192.168.1.2
```
- User: `dphoompat` (ไม่ใช่ `peyo`, ไม่ใช่ `root`)
- Key: `~/.ssh/id_ubuntu_local`
- IP: `192.168.1.2` (IP เดิม 192.168.1.203 เลิกใช้แล้ว ตั้งแต่ 28 พ.ค. 69)
- Warning `.bashrc: line 1: ฺexport: command not found` เป็นปกติ ข้ามได้

### Deploy
```
ssh -i ~/.ssh/id_ubuntu_local dphoompat@192.168.1.2 "cd /home/dphoompat/peyo-agent && bash deploy.sh"
```
- ห้ามใช้แค่ `git pull` — ต้อง `bash deploy.sh` เสมอ (ไม่งั้น static files เก่า)
- Service name: `peyo-agent` (ไม่ใช่ `gunicorn`)
- peyo-agent มี **GitHub Actions runner บน server** — push ไป main แล้ว server pull+collectstatic+restart เองภายในไม่กี่วินาที ไม่ต้อง ssh รัน deploy.sh ซ้ำ (จะ conflict) — รอ ~1 นาที แล้วตรวจ `git log -1` บน server แทน

### Instance บน server (ห้ามสับสน!)
| Instance | Path | Service | Domain |
|----------|------|---------|--------|
| peyo-agent (AIBiz) | `/home/dphoompat/peyo-agent` | `peyo-agent` | blog.kooky-shop.com |
| exam-system (ครูวิทย์) | `/home/dphoompat/exam-system` | `exam-system` | — |
| **booking-system** | `/home/dphoompat/booking-system` | `booking-system` | muskelterapeut-spa.com |
| noodee-booking (QueueFlow demo) | `/home/dphoompat/noodee-booking` | `noodee-booking` | booking.noodee-bootbiz.com |
| kanjana-booking | `/home/dphoompat/kanjana-booking` | `kanjana-booking` | — |

> 🚨 **`booking-system` = ร้านจริงที่ Bergen มีลูกค้าจริง ~50 คน — ห้ามแตะข้อมูลเด็ดขาด**
> Demo/showcase ให้ใช้ `noodee-booking` เท่านั้น

### กฎเหล็ก
- **ห้าม `git push` จนกว่าผู้ใช้จะสั่ง** (commit ได้ แต่ push ต้องรอ)
- **ห้าม deploy โดยไม่ได้รับคำสั่ง**
- "update server ครูวิทย์" = commit + push + deploy `exam-system`

---

## สิ่งที่ต้องรู้ก่อนทำงาน

โปรเจกต์นี้คือระบบ multi-agent สำหรับบริหารธุรกิจ AI Automation ครบวงจร ประกอบด้วย 14 agents แต่ละตัวมีหน้าที่ชัดเจน ทุก agent มี system prompt อยู่ใน `.claude/agents/` directory

**สินค้าและบริการ:**
- AI Chatbot สำหรับธุรกิจ
- AI Lead Generation
- AI Workflow Automation
- Custom AI Agent
- AI + Hardware Integration

**ตลาดเป้าหมาย:** SME ไทย (5-50 พนักงาน)

---

## 14 Agents

| # | Agent | ไฟล์ | บทบาทหลัก |
|---|-------|------|-----------|
| 1 | Chief of Staff | `.claude/agents/01_chief_of_staff.md` | Orchestrator หลัก, routing ทุก request |
| 2 | Hustler (Sales) | `.claude/agents/02_hustler_sales.md` | ปิดดีล B2B, qualify lead |
| 3 | AI Orchestrator | `.claude/agents/03_ai_orchestrator.md` | Technical lead, สร้างระบบ AI |
| 4 | Money Manager | `.claude/agents/04_money_manager.md` | การเงิน, บัญชี, ภาษี |
| 5 | AI Toolsmith | `.claude/agents/05_ai_toolsmith.md` | Prompt library, template, tools |
| 6 | QA Agent | `.claude/agents/06_qa_agent.md` | ตรวจคุณภาพ output ทุกชิ้น |
| 7 | Marketing Specialist | `.claude/agents/07_marketing_specialist.md` | กลยุทธ์การตลาด, content, lead gen |
| 8 | Customer Success | `.claude/agents/08_customer_success.md` | ดูแลลูกค้าหลังการขาย, retention |
| 9 | Data Analyst | `.claude/agents/09_data_analyst.md` | วิเคราะห์ข้อมูล, dashboard, insight |
| 10 | Legal Advisor | `.claude/agents/10_legal_advisor.md` | สัญญา, PDPA, compliance |
| 11 | SEO Specialist | `.claude/agents/11_seo_specialist.md` | Keyword research, on-page SEO, ranking |
| 12 | Content Writer (TH) | `.claude/agents/12_content_writer_th.md` | เขียนบทความไทยคุณภาพสูงสำหรับ SEO + lead |
| 13 | Frontend Designer | `.claude/agents/13_frontend_designer.md` | Design System, UI/UX, Color Palette, Component Library |
| 14 | AI News Scout | `.claude/agents/14_ai_news_scout.md` | ล่าข่าว AI จากค่ายใหญ่ + ส่ง brief ให้ Content Writer TH |
| 15 | Facebook Post Writer | `.claude/agents/15_facebook_post_writer.md` | เขียน Facebook Page post ภาษาไทย สำหรับบทความ/ข่าว |
| 16 | Facebook Group Writer | `.claude/agents/16_facebook_group_writer.md` | เขียน Facebook Group post แบบ community ไม่ขายตรง |
| 17 | Instagram Caption Writer | `.claude/agents/17_instagram_caption_writer.md` | เขียน Instagram caption + hashtags 20-30 tags |
| 18 | LINE Broadcast Writer | `.claude/agents/18_line_broadcast_writer.md` | เขียนข้อความ LINE Broadcast สั้น กระชับ มี CTA |
| 19 | Healthcare Content Writer | `.claude/agents/19_healthcare_content_writer.md` | บทความสำหรับคลินิก/โรงพยาบาล tone professional |
| 20 | E-commerce Content Writer | `.claude/agents/20_ecommerce_content_writer.md` | บทความสำหรับร้านค้าออนไลน์ tone casual FOMO |
| 21 | Hospitality Content Writer | `.claude/agents/21_hospitality_content_writer.md` | บทความสำหรับโรงแรม/รีสอร์ท tone aspirational |
| 22 | Beauty & Wellness Writer | `.claude/agents/22_beauty_wellness_writer.md` | บทความสำหรับร้านนวด/สปา tone warm relatable |
| 23 | HR & Education Writer | `.claude/agents/23_hr_education_writer.md` | บทความสำหรับ HR/โรงเรียน tone data-driven |
| 24 | Creator & Coach Writer | `.claude/agents/24_creator_coach_writer.md` | บทความสำหรับโค้ช/อาจารย์ออนไลน์ tone inspirational |
| 25 | Graphic Designer | `.claude/agents/25_graphic_designer.md` | Technical diagram, infographic, banner, cover image, presentation deck |
| 26 | Market Research Analyst | `.claude/agents/26_market_research_analyst.md` | วิจัยตลาดซอฟต์แวร์ไทย: คู่แข่ง, pricing benchmark, market sizing, gap analysis — ข้อมูลจริงมีแหล่งอ้างอิงเท่านั้น |

## Skills (ใน `.claude/skills/`)

| Skill | ใช้เมื่อไหร่ |
|-------|------------|
| `agent-creator` | Meta-skill — สร้าง/audit agent ตาม rubric 10/10 พร้อมลงทะเบียนใน CLAUDE.md |
| `skill-creator` | Meta-skill — สร้าง skill ใหม่แบบมีมาตรฐาน พร้อมลงทะเบียนใน CLAUDE.md |
| `scrape-claude-docs` | ดึงข้อมูลจาก code.claude.com/docs เพื่อใช้เป็น source material |
| `scrape-ai-news` | ดึงข่าว AI ล่าสุดจากค่ายใหญ่ + return brief JSON พร้อม summary ไทย (ใช้ใน Workflow F) |
| `seo-keyword-research-th` | วิจัย keyword ภาษาไทย ก่อนเขียนทุกบทความ |
| `django-blog-publisher` | โพสบทความเข้า Django blog app พร้อม SEO meta |
| `auto-diagram-generator` | Generate diagram Pillow ทุก H2 section อัตโนมัติ + image_brief.md พร้อม SEO filename |
| `flux-cover-image` | Generate cover image FLUX + หนูดี + Pillow text overlay → WebP พร้อม alt text |
| `diagram-to-blog` | Upload diagram เข้า Django media + inject `<img>` tag เข้าบทความ draft |
| `social-banner-template` | สร้าง banner 3 platform (Facebook/Instagram/LINE) พร้อมกันใน 10 นาที |
| `visual-qa-checklist` | ตรวจ visual 15 ข้อ — brand, SEO, technical, content ก่อน deliver ทุกชิ้น |
| `screenshot-tutorial-generator` | ถ่ายหน้าจอ browser จริงทีละ step ด้วย Playwright + annotate ด้วย Pillow สำหรับบทความ how-to |

---

## วิธี Activate Agent

### Explicit Activation (พิมพ์ตรง):
```
Activate Chief of Staff - [คำถาม]
Activate Marketing Specialist - [คำถาม]
Activate Customer Success - [คำถาม]
Activate Data Analyst - [คำถาม]
Activate Legal Advisor - [คำถาม]
Activate SEO Specialist - [คำถาม]
Activate Content Writer - [คำถาม]
Activate Hustler - [คำถาม]
Activate AI Orchestrator - [คำถาม]
Activate Money Manager - [คำถาม]
Activate AI Toolsmith - [คำถาม]
Activate QA Agent - [คำถาม]
Activate Frontend Designer - [คำถาม]
Activate AI News Scout - [คำถาม]
Activate Graphic Designer - [คำถาม]
Activate Market Research - [คำถาม]
```

### Alias สั้น:
| Alias | Agent |
|-------|-------|
| `หนูดี - [คำถาม]` | Chief of Staff |

ตัวอย่าง: `หนูดี - สรุปสถานะธุรกิจวันนี้`

### เรียกผ่าน Claude Code Subagent System (native)
แต่ละ agent ใน `.claude/agents/` มี frontmatter `name:` ที่ Claude Code ใช้ระบุ subagent ได้
เรียกใช้ด้วยชื่อ slug:

| Slug | Agent |
|------|-------|
| `chief-of-staff` | Chief of Staff |
| `hustler-sales` | Hustler (Sales) |
| `ai-orchestrator` | AI Orchestrator |
| `money-manager` | Money Manager |
| `ai-toolsmith` | AI Toolsmith |
| `qa-agent` | QA Agent |
| `marketing-specialist` | Marketing Specialist |
| `customer-success` | Customer Success |
| `data-analyst` | Data Analyst |
| `legal-advisor` | Legal Advisor |
| `seo-specialist` | SEO Specialist |
| `content-writer-th` | Content Writer (TH) |
| `frontend-designer` | Frontend Designer |
| `ai-news-scout` | AI News Scout |
| `graphic-designer` | Graphic Designer |
| `market-research-analyst` | Market Research Analyst |

### Auto-routing ผ่าน Chief of Staff:
```
ปรึกษาเรื่อง [topic]
```
Chief of Staff จะเลือก agent ที่เหมาะสมให้อัตโนมัติ

---

## Routing Logic (Chief of Staff ใช้)

| หัวข้อ | Primary Agent | Supporting Agents |
|--------|--------------|-------------------|
| ภาพรวมธุรกิจ | Chief of Staff | — |
| เปิด campaign ใหม่ | Marketing Specialist | Money Manager, Data Analyst, Hustler |
| ลูกค้าจะต่อสัญญาไหม | Customer Success | Data Analyst, Hustler |
| ตรวจสอบสัญญา | Legal Advisor | Money Manager, Hustler |
| ทำไมรายได้ลด | Data Analyst | Customer Success, Hustler |
| สร้างระบบ AI | AI Orchestrator | AI Toolsmith, QA |
| ปิดดีลลูกค้าใหม่ | Hustler | Legal, Money Manager |
| ปัญหาการเงิน | Money Manager | Data Analyst, Legal |
| ทำคอนเทนต์ SEO / blog | Marketing Specialist | SEO, Content Writer, Frontend Designer, AI Toolsmith, QA |
| Design System / UI/UX | Frontend Designer | Marketing Specialist, AI Orchestrator, QA |
| Keyword research / on-page SEO | SEO Specialist | Content Writer, Data Analyst |
| เขียนบทความภาษาไทย | Content Writer (TH) | SEO, AI Toolsmith, QA |
| ข่าว AI / AI News Pipeline | AI News Scout | Content Writer TH, QA, Data Analyst |
| Diagram / Infographic / Banner / Graphic | Graphic Designer | Content Writer TH, Marketing Specialist, Frontend Designer, QA |
| วิจัยตลาด / คู่แข่ง / ราคา benchmark | Market Research Analyst | Marketing Specialist, Hustler, Money Manager, Data Analyst |

---

## Critical Workflows

ดูรายละเอียดเต็มใน `workflows/`:

- **Workflow A:** Marketing → Sales → Customer Success
- **Workflow B:** Customer Issue → Engineering → Fix
- **Workflow C:** Contract Negotiation (Sales → Money → Legal → Sign)
- **Workflow D:** Data-Driven Decision Loop
- **Workflow E:** Content Pipeline (SEO → Write → QA → Publish → Track)
- **Workflow F:** AI News Pipeline (Scout → Write → QA → Draft → Human Publish)

---

## 🗺️ แผนพัฒนาต้องตรงกับความจริงเสมอ (บังคับ ตั้งแต่ 2026-08-26)

**แหล่งความจริงเดียว:** `dashboard/roadmap.py` · **หน้าจอ:** `/owner/roadmap/` (superuser เท่านั้น คนอื่นได้ 404)

1. **งานที่ไม่มีใน `roadmap.py` = งานนอกแผน ต้องถามเจ้าของก่อนลงมือ**
2. ปิดงานเรื่องไหนเสร็จ **เปลี่ยน `status` เป็น `DONE` ในคอมมิตเดียวกับโค้ด** ห้ามค้างไว้ทำทีหลัง
3. ขึ้นเฟสใหม่ต้องแก้ `CURRENT` ด้วย — เทส `dashboard.tests_roadmap` บังคับว่าต้องมีเฟส `IN_PROGRESS` เพียงเฟสเดียวเสมอ
4. เรื่องที่ติดรอเจ้าของใส่ `DECISIONS` (ขึ้นกล่องแดงพร้อมนับวันที่ค้าง) · หนี้ทางเทคนิคใส่ `TECH_DEBT`
5. สถานะเป็นสิ่งที่ **คนกำหนด** ไม่ใช่ระบบเดา — ตัวเลขจริงจาก DB แสดงคู่กันเพื่อเทียบว่า "แผนบอกเสร็จ" กับ "มีคนใช้จริงหรือยัง" ตรงกันไหม

**มีของบังคับจริง 2 ชั้น ไม่ได้พึ่งความจำ:**

| ชั้น | กลไก | ทำอะไร |
|---|---|---|
| กันตั้งแต่ต้นทาง | git hook `.githooks/pre-commit` | commit ที่แตะ `models.py` / `urls.py` / `migrations/` / `.claude/agents,skills/` แต่ไม่แตะ `roadmap.py` จะถูก **บล็อก** |
| ให้เจ้าของจับได้เอง | แถบเตือนบนหน้า roadmap | แผนไม่ถูกแก้เกิน 7 วัน ขึ้นแถบแดง (`STALE_AFTER_DAYS`) |

- **clone ใหม่ต้องสั่ง `git config core.hooksPath .githooks` หนึ่งครั้ง** ไม่งั้น hook ไม่ทำงาน
- ข้าม hook ได้ด้วย `SKIP_ROADMAP_CHECK=1 git commit ...` — ใช้เฉพาะเวลาจำเป็นจริง ไม่ใช่เพื่อความเร็ว
- รันเทส: `$env:USE_MYSQL="False"; venv\Scripts\python.exe manage.py test dashboard.tests_roadmap`
  (ต้อง override เพราะ user `peyo` สร้าง test database บน MySQL ไม่ได้)

> ระบบนี้ยกมาจากโปรเจกต์ StockProject (`MainProject/core/roadmap.py`) ตามที่เจ้าของสั่ง 26 ส.ค. 2569

---

## 📝 Content Backlog System

ผู้ใช้เพิ่ม topic ใน `content_backlog/BACKLOG.md` → หนูดีหยิบไปทำผ่าน Workflow E
เริ่มได้ด้วย: `หนูดี - process backlog` (ดู BACKLOG.md สำหรับคำสั่งเต็ม)

**Rule สำคัญ:** หนูดี publish ทุกบทความเป็น `status="draft"` เสมอ — ผู้ใช้กด publish เองใน Django admin

---

## Approval Matrix

| การตัดสินใจ | เจ้าของ | ผู้อนุมัติ |
|------------|---------|-----------|
| Marketing campaign < 5K | Marketing | ตัวเอง |
| Marketing campaign 5K-20K | Marketing | Money Manager |
| Marketing campaign > 20K | Marketing | CEO |
| Discount < 10% | Sales | ตัวเอง |
| Discount 10-20% | Sales | Chief of Staff |
| Discount > 20% | Sales | CEO |
| Refund < 5K | CS | ตัวเอง |
| Refund 5K-20K | CS | Money Manager |
| Contract < 100K | Sales | Legal |
| Contract 100K-500K | Sales | Legal + Money |
| Contract > 500K | Sales | Legal + Money + CEO |

---

## Communication Cadence

| ความถี่ | รูปแบบ |
|--------|-------|
| ทุกวัน 9:00 | แต่ละ agent ส่ง daily stand-up → Chief of Staff |
| ทุกวัน 9:30 | CoS รวบรวม → Executive Summary ส่ง CEO |
| ทุกศุกร์ 17:00 | Weekly Strategic Review (CEO + CoS + 3 agents) |
| วันที่ 1 ของเดือน | Monthly Business Review (all agents) |
| ทุก 3 เดือน | Quarterly Planning (2 วัน) |

---

## When to Add Each Agent

| Revenue MRR | Agent ที่เพิ่ม |
|-------------|--------------|
| ตอนนี้ | 6 agents พื้นฐาน (1-6) |
| 30K+ | Marketing Specialist (7) |
| 50K+ | Customer Success (8) |
| 100K+ | Data Analyst (9) |
| 200K+ | Legal Advisor (10) |

---

## ไฟล์สำคัญ

- `agent_expansion_v2.md` — เอกสาร spec เต็ม (single source of truth)
- `.claude/agents/` — System prompts ของแต่ละ agent (Claude Code subagent format พร้อม frontmatter)
- `.claude/skills/` — Reusable skills (SKILL.md ในแต่ละ subfolder)
- `workflows/` — Workflow diagrams และ SLAs
