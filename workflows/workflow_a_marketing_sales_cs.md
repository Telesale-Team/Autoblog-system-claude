# Workflow A: Marketing → Sales → Customer Success

**ประเภท:** Revenue Pipeline
**เจ้าของ:** Chief of Staff
**SLA รวม:** MQL → Onboarded ภายใน 30 วัน

---

## Flow Diagram

```
Marketing Specialist
    │
    │ MQL (พร้อม lead score + context)
    ↓
Hustler (Sales)     ← ต้อง respond ภายใน 2 ชั่วโมง
    │
    │ Qualify (BANT)
    ├─── Not Qualified → กลับ Marketing (feedback)
    │
    │ SQL confirmed
    │ Discovery → Demo → Proposal → Negotiation
    │
    │ Closed Won
    ↓
Customer Success    ← Handoff ภายใน 48 ชั่วโมง
    │
    │ Onboarding (30 วัน)
    │ Adoption (90 วัน)
    │ Value Realization (180 วัน)
    │ Renewal (365 วัน)
    │
    ├─── Case Study + Testimonial
    ↓
Marketing Specialist ← (content สำหรับ social proof)
```

---

## Step-by-step

### Step 1: Marketing → Sales Handoff

**Marketing ส่งให้ Sales:**
```
Lead Name: [ชื่อ]
Company: [บริษัท]
Source Channel: [LinkedIn / Referral / Organic / etc.]
Lead Score: [0-100]
Interest Signals: [สิ่งที่ engage]
Engagement History: [action ที่ทำ]
Pain Point (ที่รู้): [ถ้ามี]
Recommended Next Action: [call / email / demo]
```

**SLA:** Marketing ส่งภายใน 24 ชั่วโมงหลังเป็น MQL

### Step 2: Sales Qualify

**BANT Check:**
- Budget: มีงบหรือไม่?
- Authority: ตัดสินใจได้เอง?
- Need: ปัญหาชัดเจน urgent ไหม?
- Timeline: อยากเริ่มเมื่อไหร่?

**SLA:** Sales respond MQL ภายใน 2 ชั่วโมง

### Step 3: Sales Process

| Stage | Action | SLA |
|-------|--------|-----|
| Discovery | Call 30-60 min | ภายใน 24 ชั่วโมงหลัง qualify |
| Demo | Show solution | ภายใน 3 วัน |
| Proposal | ส่ง proposal | ภายใน 48 ชั่วโมงหลัง demo |
| Negotiation | Back-and-forth | ไม่เกิน 14 วัน |
| Close | Sign + payment | Day 0 |

### Step 4: Sales → CS Handoff

**Sales ส่งให้ CS (ภายใน 48 ชั่วโมงหลัง close):**
```
Customer Name: [ชื่อ]
Company: [บริษัท]
Package: [ที่ซื้อ]
Contract Value: [มูลค่า]
Payment Terms: [เงื่อนไข]
Pain Points: [ปัญหาที่แก้]
Success Criteria: [ที่ลูกค้าต้องการ]
Key Contacts: [ชื่อ + role]
Quirks/Notes: [สิ่งที่ต้องรู้]
Start Date: [วันเริ่ม]
```

### Step 5: CS Onboarding

ดูรายละเอียดใน [08_customer_success.md](../agents/08_customer_success.md) — Onboarding Playbook

### Step 6: Feedback Loop

**CS → Marketing (สม่ำเสมอ):**
- Case study materials
- Customer testimonials
- Pain points ที่พบบ่อย (ใช้ปรับ content)

**Sales → Marketing (รายเดือน):**
- MQL quality score
- Which channels produce best leads
- Common objections (ใช้ปรับ content)

---

## KPIs ของ Workflow นี้

| Metric | เป้า |
|--------|------|
| MQL → SQL rate | > 30% |
| SQL → Close rate | > 20% |
| Time MQL → Close | < 30 วัน |
| Time Close → Onboarded | < 14 วัน |
| Onboarding satisfaction | > 4/5 |
