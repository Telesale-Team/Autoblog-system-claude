# AI Automation Business — 13-Agent System

ระบบ AI Agent สำหรับธุรกิจ AI Automation Specialist ที่ขายระบบ AI ให้ SME ไทย

**Version:** 2.2 | **Updated:** 2026-05-14

---

## สิ่งที่ต้องรู้ก่อนทำงาน

โปรเจกต์นี้คือระบบ multi-agent สำหรับบริหารธุรกิจ AI Automation ครบวงจร ประกอบด้วย 10 agents แต่ละตัวมีหน้าที่ชัดเจน ทุก agent มี system prompt อยู่ใน `.claude/agents/` directory

**สินค้าและบริการ:**
- AI Chatbot สำหรับธุรกิจ
- AI Lead Generation
- AI Workflow Automation
- Custom AI Agent
- AI + Hardware Integration

**ตลาดเป้าหมาย:** SME ไทย (5-50 พนักงาน)

---

## 13 Agents

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

## Skills (ใน `.claude/skills/`)

| Skill | ใช้เมื่อไหร่ |
|-------|------------|
| `agent-creator` | Meta-skill — สร้าง/audit agent ตาม rubric 10/10 พร้อมลงทะเบียนใน CLAUDE.md |
| `skill-creator` | Meta-skill — สร้าง skill ใหม่แบบมีมาตรฐาน พร้อมลงทะเบียนใน CLAUDE.md |
| `scrape-claude-docs` | ดึงข้อมูลจาก code.claude.com/docs เพื่อใช้เป็น source material |
| `seo-keyword-research-th` | วิจัย keyword ภาษาไทย ก่อนเขียนทุกบทความ |
| `django-blog-publisher` | โพสบทความเข้า Django blog app พร้อม SEO meta |

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

---

## Critical Workflows

ดูรายละเอียดเต็มใน `workflows/`:

- **Workflow A:** Marketing → Sales → Customer Success
- **Workflow B:** Customer Issue → Engineering → Fix
- **Workflow C:** Contract Negotiation (Sales → Money → Legal → Sign)
- **Workflow D:** Data-Driven Decision Loop
- **Workflow E:** Content Pipeline (SEO → Write → QA → Publish → Track)

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
