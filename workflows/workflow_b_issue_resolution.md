# Workflow B: Customer Issue Resolution

**ประเภท:** Support + Engineering
**เจ้าของ:** Customer Success
**SLA:** ตาม Priority Level

---

## Flow Diagram

```
Customer (แจ้งปัญหา)
    ↓
Customer Success
    │ Triage → กำหนด Priority
    │
    ├── P1/P2 (Critical/High) ─────────────────────────┐
    │                                                    │
    │ P3/P4 (Medium/Low)                                 │
    │   │                                                │
    │   ↓                                                ↓
    │  CS แก้เองได้?           AI Orchestrator (Engineering)
    │   ├── Yes → แก้ + แจ้งลูกค้า       │
    │   └── No  ─────────────────────────┘
    │                                    │
    │                              QA Agent (verify fix)
    │                                    │
    └────────────────────────────────────┘
                                         │
                               Customer Success
                                         │
                               แจ้งลูกค้า + ปิด ticket
```

---

## Step-by-step

### Step 1: CS รับแจ้งและ Triage

**ข้อมูลที่ต้องเก็บ:**
```
Ticket ID: [auto]
Customer: [ชื่อ]
Reported: [วันเวลา]
Description: [รายละเอียดปัญหา]
Reproduction Steps: [วิธีทำให้เกิดซ้ำ]
Impact: [กระทบอะไร]
Workaround Available: [Yes/No]
Priority: [P1/P2/P3/P4]
```

### Step 2: Priority SLA

| Priority | ความหมาย | CS Response | Resolution |
|----------|---------|-------------|------------|
| P1 - Critical | ระบบล่มสนิท, data loss risk | 30 นาที | 4 ชั่วโมง |
| P2 - High | Feature หลักใช้ไม่ได้ | 2 ชั่วโมง | 24 ชั่วโมง |
| P3 - Medium | Bug ที่มี workaround | 24 ชั่วโมง | 1 สัปดาห์ |
| P4 - Low | Cosmetic, docs | 72 ชั่วโมง | Next sprint |

### Step 3: CS → Engineering Escalation

**ส่งให้ AI Orchestrator:**
```
Ticket ID: [ID]
Priority: [P1/P2/P3/P4]
Customer Impact: [กระทบยังไง]
Reproduction Steps: [ขั้นตอน]
Expected Behavior: [ควรเป็นยังไง]
Actual Behavior: [เป็นยังไง]
Urgency: [ทำไมถึง urgent]
Customer Deadline: [ถ้ามี]
```

### Step 4: Engineering → QA

AI Orchestrator ส่ง fix ให้ QA ตรวจ:
- Unit tests pass
- No regression
- Fix verified on staging

### Step 5: QA → CS

QA แจ้ง CS เมื่อ approve:
- Fix description
- Deployment date/time
- Testing done
- Known limitations (ถ้ามี)

### Step 6: CS → Customer

Template สำหรับแจ้งลูกค้า:
```
สวัสดีครับ/ค่ะ คุณ[ชื่อ]

ขอแจ้งให้ทราบว่าปัญหา [ชื่อปัญหา] ที่แจ้งเมื่อ [วันที่] 
ได้รับการแก้ไขเรียบร้อยแล้วครับ/ค่ะ

สาเหตุ: [อธิบายสั้น ๆ]
การแก้ไข: [สิ่งที่ทำ]
ผลลัพธ์: ระบบกลับมาทำงานปกติแล้ว

กรุณาทดสอบใช้งานและแจ้งกลับมาหากยังพบปัญหา

ขออภัยในความไม่สะดวกครับ/ค่ะ
[ชื่อ CS]
```

---

## Escalation Rules

| สถานการณ์ | Escalate ไปที่ |
|-----------|--------------|
| P1 ไม่ resolve ใน 2 ชั่วโมง | CEO |
| ลูกค้า threaten จะ cancel | Chief of Staff |
| Data breach | Legal + CEO ทันที |
| Repeated P1 ลูกค้าเดิม | Chief of Staff |

---

## Post-Mortem (สำหรับ P1/P2)

ทำหลัง resolve ภายใน 48 ชั่วโมง:
1. Timeline ของ incident
2. Root cause
3. Impact (จำนวนลูกค้า, duration)
4. Fix ที่ทำ
5. Prevention (จะป้องกันอนาคตยังไง)
