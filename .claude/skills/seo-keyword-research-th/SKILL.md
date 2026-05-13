---
name: seo-keyword-research-th
description: Research Thai-language SEO keywords for AI Automation content. Use when SEO Specialist needs to find primary/secondary keywords, search intent, and competitor analysis before content creation.
---

# Skill: SEO Keyword Research (Thai)

วิจัย keyword ภาษาไทยสำหรับเว็บไซต์ AI Automation
output คือ Keyword Brief ที่ Content Writer เอาไปเขียนได้เลย

## เมื่อไหร่ใช้
- ก่อนเริ่มเขียนบทความใหม่ทุกครั้ง
- ทำ topic cluster planning รายไตรมาส
- ตรวจ keyword gap เทียบคู่แข่ง

## Input ที่ต้องการ
- หัวข้อกว้างๆ เช่น "Claude Code", "AI Chatbot SME"
- ภาษาเป้าหมาย: ไทย (อาจมี keyword อังกฤษปนเพราะคนไทยชอบค้นแบบ "Claude Code คืออะไร")

## ขั้นตอน

### Step 1: Seed keyword expansion
จากหัวข้อตั้งต้น → ขยายเป็น 20-30 variations:
- Question form: "X คืออะไร", "X ใช้ยังไง", "X ดีไหม", "วิธี X"
- Comparison: "X vs Y", "X กับ Y ต่างกันยังไง"
- Commercial: "X ราคา", "X ฟรี", "X agency", "จ้างทำ X"
- Problem-solving: "ปัญหา X", "X ไม่ทำงาน", "แก้ X"

### Step 2: ใช้ WebSearch ตรวจ SERP จริง
สำหรับแต่ละ keyword สำคัญ:
```
WebSearch("<keyword>")
```
ดู:
- Top 10 results เป็นใคร (คู่แข่ง)
- Featured snippet มีไหม
- People Also Ask ถามอะไร
- Related searches ด้านล่าง

### Step 3: ประเมิน intent + difficulty (manual)
จัดประเภทแต่ละ keyword:
| Intent | สัญญาณ |
|--------|--------|
| Informational | "คืออะไร", "ยังไง", "วิธี" |
| Commercial | "เปรียบเทียบ", "รีวิว", "ดีไหม" |
| Transactional | "ราคา", "ซื้อ", "จ้าง", "สมัคร" |
| Navigational | ชื่อ brand เฉพาะ |

ประเมิน difficulty (low/medium/high) จาก:
- Top 10 มี domain ใหญ่ (DA สูง) เยอะแค่ไหน
- มี ads เยอะไหม (= keyword มีมูลค่า แต่แข่งสูง)
- Content depth ของ top 3

### Step 4: Output Keyword Brief
สร้างไฟล์ `content_briefs/<topic-slug>.md`:

```markdown
# Keyword Brief: <หัวข้อ>

**Created:** YYYY-MM-DD
**Target audience:** SME ไทย / ...

## Primary Keyword
- **Keyword:** <คำหลัก>
- **Estimated intent:** Informational
- **Difficulty:** Medium
- **Why this:** <เหตุผลที่เลือก>

## Secondary Keywords (ใส่ใน H2/H3)
1. ...
2. ...
3. ...

## People Also Ask (ใช้เป็น FAQ section)
- ...
- ...

## Top 3 Competitors
| Rank | URL | Word count | Strength | Weakness |
|------|-----|-----------|----------|----------|

## Content Angle ที่เราชนะได้
- <จุดที่เราทำได้ดีกว่า top 3>

## Suggested
- **Title:** <≤60 chars, มี primary keyword>
- **Meta description:** <≤155 chars + CTA>
- **Slug:** <english-kebab-case>
- **Word count target:** 1500-2000
- **Internal links to:** [list pages]
```

## Tools เสริม (ถ้ามี budget)
- Ahrefs / SEMrush — exact volume + KD
- Ubersuggest — free tier ใช้ได้บ้าง
- Google Trends — เช็ค trend ขึ้น/ลง
- AnswerThePublic — questions

## หมายเหตุ
- คนไทยพิมพ์ผิดเยอะ → เก็บ misspelling variations ด้วย
- บาง keyword ภาษาอังกฤษ volume สูงกว่าไทย แต่ converting ต่ำกว่า → เลือกตาม intent
- อย่าเลือก keyword DA สูงๆ ถ้าเว็บเรายังใหม่ → เริ่ม long-tail ก่อน
