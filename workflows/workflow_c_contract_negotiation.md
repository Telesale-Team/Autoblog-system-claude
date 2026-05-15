# Workflow C: Contract Negotiation

**ประเภท:** Sales + Legal + Finance
**เจ้าของ:** Hustler (Sales)
**SLA:** Sign ภายใน 14 วันหลัง verbal agreement

---

## Flow Diagram

```
Hustler (Sales)
    │ Verbal agreement reached
    │ Draft initial contract
    ↓
Money Manager
    │ Review financial terms
    │ - Pricing OK?
    │ - Payment terms OK?
    │ - Revenue recognition OK?
    ↓
Legal Advisor
    │ Review legal terms
    │ - Limitation of liability
    │ - IP ownership
    │ - PDPA compliance
    │ - SLA terms
    ↓
Hustler (Sales)
    │ Negotiate with customer
    │ (ถ้ามีแก้ไข → วนกลับ Money/Legal)
    ↓
Sign (ทั้งสองฝ่าย)
    ↓
Customer Success
    (Onboarding begins)
```

---

## Step-by-step

### Step 1: Sales Draft Contract

เลือก template ที่เหมาะสม:
| Deal size | Template |
|-----------|---------|
| < 50,000 | Service Agreement |
| 50K - 500K | MSA + SOW |
| > 500K | Full MSA + SOW + SLA |
| MRR / รายเดือน | Subscription Agreement |
| ก่อนคุยรายละเอียด | NDA ก่อน |

### Step 2: Money Manager Review

**เช็คประเด็นการเงิน:**
- [ ] ราคา = ที่ตกลงกัน
- [ ] Payment terms (30/60/90 วัน)
- [ ] Milestone payment schedule
- [ ] Late payment penalty
- [ ] Tax (VAT, withholding tax)
- [ ] Currency + exchange rate (ถ้า international)
- [ ] Refund policy

**SLA:** Money Manager ตอบภายใน 24 ชั่วโมง

### Step 3: Legal Advisor Review

**เช็คประเด็นกฎหมาย:**
- [ ] Limitation of liability clause
- [ ] IP ownership ชัดเจน
- [ ] Confidentiality / NDA terms
- [ ] Termination clause (ทั้งสองฝ่าย)
- [ ] Force majeure
- [ ] PDPA / data processing terms
- [ ] SLA + penalty (realistic?)
- [ ] Governing law = ไทย
- [ ] Dispute resolution process

**Output:** Risk rating 🔴🟡🟢 + suggested changes

**SLA:** Legal Advisor ตอบภายใน 24 ชั่วโมง

### Step 4: Approval Gate

| Contract Value | ต้องได้ approval จาก |
|---------------|---------------------|
| < 100,000 | Legal OK เท่านั้น |
| 100K - 500K | Legal + Money Manager |
| > 500K | Legal + Money + CEO |

### Step 5: Negotiation

Sales negotiate กับลูกค้า:
- เปลี่ยนได้ (ไม่ต้อง re-review): minor wording
- ต้อง re-review: ทุกที่เปลี่ยน financial / liability terms

### Step 6: Sign + File

หลัง sign:
- [ ] สำเนาให้ลูกค้า
- [ ] เก็บต้นฉบับ (digital + physical)
- [ ] แจ้ง Money Manager (update billing)
- [ ] แจ้ง CS (เริ่ม onboarding)
- [ ] อัพเดท CRM

---

## Common Negotiation Points

| ลูกค้าขอ | ตอบ |
|---------|-----|
| Unlimited liability | ต้านทาน — cap ที่ 12 months revenue |
| Source code ownership | ได้ แต่เพิ่มราคา 30-50% |
| 99.9% SLA | ต้านทาน — เสนอ 99% + penalty credit |
| Net 90 payment | พยายาม Net 30-45 |
| Unlimited revision | ต้านทาน — กำหนด revision ใน SOW |

---

## Red Lines (ห้ามเซ็น)

- Unlimited liability ทุกกรณี
- Liquidated damages เกิน contract value
- ลูกค้าเป็นเจ้าของ IP ทั้งหมดโดยไม่มีค่าตอบแทนเพิ่ม
- Warranty ไม่สิ้นสุด
- Governing law ต่างประเทศ (โดยไม่มีเหตุผล)
