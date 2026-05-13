# Workflow D: Data-Driven Decision

**ประเภท:** Analytics + Strategy
**เจ้าของ:** Data Analyst
**ความถี่:** รายสัปดาห์ / on-demand

---

## Flow Diagram

```
Data Analyst
    │ Collect + analyze data
    │ Generate insight
    ↓
Chief of Staff
    │ Validate insight
    │ Determine action needed
    │ Identify relevant agents
    ↓
Relevant Agents
    │ Implement action
    │ (Marketing / Sales / CS / Engineering)
    ↓
Data Analyst
    │ Measure results
    │ Compare vs hypothesis
    ↓
Iterate (ถ้าจำเป็น)
```

---

## Step-by-step

### Step 1: Data Collection

**Data Analyst เก็บจาก:**
- Google Analytics (web traffic)
- CRM (pipeline, deals)
- Financial system (revenue, cash)
- Product system (usage, errors)
- Customer feedback (NPS, CSAT)

**ความถี่:**
| ข้อมูล | ความถี่ |
|--------|--------|
| Revenue snapshot | Daily |
| Pipeline update | Weekly |
| Marketing performance | Weekly |
| Customer health | Weekly |
| Full business review | Monthly |
| Cohort analysis | Monthly |
| Strategic deep dive | Quarterly |

### Step 2: Insight Generation

**Format Insight ที่ดี:**
```
🔍 Finding: [1 sentence — lead with insight, not data]

📊 Data: [ตัวเลขสนับสนุน]

💡 Why it matters: [business impact]

✅ Recommended Action: [สิ่งที่ควรทำ]

📏 How to measure: [วิธีวัดผล]
```

**ตัวอย่าง:**
```
🔍 Finding: LinkedIn เป็น channel ที่ produce MQL ดีที่สุด
            แต่ใช้เวลา 3x มากกว่า Facebook

📊 Data: LinkedIn: 12 MQL/เดือน, conversion 35%
         Facebook: 8 MQL/เดือน, conversion 12%
         Time spent: LinkedIn 10 ชม, Facebook 3 ชม

💡 Why it matters: ถ้า optimize time allocation จะเพิ่ม MQL ได้ 40%

✅ Recommended: ลด Facebook 50%, เพิ่ม LinkedIn 30%
               ประหยัดเวลา + เพิ่ม quality lead

📏 Measure: MQL volume + conversion rate หลัง 4 สัปดาห์
```

### Step 3: Chief of Staff Validation

CoS เช็ค:
- Insight สมเหตุสมผลไหม?
- มี confounding factor ที่ Data Analyst พลาดไหม?
- Action อยู่ใน budget + strategy?
- ใคร (agent ไหน) ต้อง act?

### Step 4: Agent Action

CoS assign ให้ agent ที่เกี่ยวข้อง:
```
To: [Agent name]
Insight: [summary]
Recommended Action: [สิ่งที่ต้องทำ]
Deadline: [วันที่]
Success Metric: [วัดผลยังไง]
```

### Step 5: Measure + Iterate

Data Analyst ติดตาม:
- ผลลัพธ์จริง vs คาด
- มี unexpected effect ไหม?
- ควร continue / stop / adjust?

---

## Triggered Insights (Auto-alert)

Data Analyst alert อัตโนมัติเมื่อ:

| เงื่อนไข | Alert ไปที่ |
|---------|-----------|
| MRR drop > 10% MoM | CEO + CoS |
| Customer health < 40 (Critical) | CS + CoS |
| Pipeline value drop > 30% | Sales + CoS |
| CAC เพิ่ม > 50% | Marketing + Money Manager |
| Churn rate > 5%/เดือน | CS + CEO |
| Cash runway < 3 เดือน | CEO + Money Manager |

---

## Decision Framework

ใช้เมื่อต้องตัดสินใจจาก data:

| ข้อมูลที่มี | วิธีตัดสินใจ |
|-----------|------------|
| ชัดเจน + confidence สูง | Act immediately |
| ชัดเจน แต่ confidence ต่ำ | Test ก่อน (A/B test) |
| ไม่ชัดเจน + impact สูง | Collect more data |
| ไม่ชัดเจน + impact ต่ำ | Best guess + monitor |
