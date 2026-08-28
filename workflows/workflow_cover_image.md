# Workflow: สร้างภาพหน้าปกบทความด้วย AI (ฟรี)

**เวลาที่ใช้:** 5–10 นาทีต่อบทความ
**เครื่องมือ:** Bing Image Creator (ฟรี) + Canva (ฟรี)
**ผลลัพธ์:** ภาพ JPG/PNG ขนาด 1200×628px พร้อม upload ขึ้น blog

---

## เครื่องมือที่ต้องเตรียม (ครั้งแรกครั้งเดียว)

### 1. Bing Image Creator

- เข้า: **https://www.bing.com/images/create**
- Login ด้วย Microsoft account (Hotmail / Outlook ก็ได้)
- ได้ 100 credits ฟรี (แต่ละภาพใช้ 1 credit, ถ้าหมดยังใช้ได้ช้าลง)

### 2. Canva

- เข้า: **https://www.canva.com**
- สมัคร/Login ฟรี
- ใช้สำหรับใส่ตัวหนังสือและ resize

---

## ขั้นตอน

### Step 1 — เตรียม Prompt จาก Headline บทความ

คัดลอก **headline** ของบทความที่จะทำ แล้วนำมาแต่ง prompt ตาม template นี้:

**Template Prompt (EN):**

```
Professional blog cover image for Thai business article about [TOPIC].
Dark navy blue background (#0f1b35), gold accent elements.
Modern minimalist style. No text in image.
Clean, corporate, digital technology feel.
High quality, 16:9 ratio.
```

**แทนที่ [TOPIC] ด้วยหัวข้อสั้นๆ ของบทความ:**

| บทความ                                          | [TOPIC] ที่ใช้                            |
| ----------------------------------------------------- | ----------------------------------------------- |
| ธุรกิจไม่ปรับตัว 70% หายไป       | business competition AI transformation Thailand |
| คู่แข่งใช้ AI แล้ว                      | business rivalry AI advantage competition       |
| ทุกวันไม่มี AI เสียเงิน            | money leaking business without AI automation    |
| พนักงานลาออกงานซ้ำซาก            | employee burnout repetitive work automation     |
| ลูกค้าตัดสินใจ 5 นาที               | customer response time online business chat     |
| ตอบช้า รีวิวแย่ Google ลดอันดับ | slow response bad review Google ranking         |
| ต้นทุนจ้างคนขึ้นทุกปี            | rising labor cost automation solution           |
| Claude for Small Business                             | AI tools small business software integration    |
| Meta ทิ้ง Open Source                             | AI industry shift technology news               |
| GPT-5.5 พูดผิดน้อยลง                      | AI accuracy improvement ChatGPT update          |
| Gemini Omni สร้างวิดีโอ                    | AI video generation Google technology           |
| Gemini ลดราคา                                   | AI pricing affordable technology                |
| Mistral Small 4                                       | open source AI model free technology            |
| Grok Build                                            | AI coding tool developer software               |
| ChatGPT จัดการการเงิน                    | AI financial management personal finance        |

---

### Step 2 — สร้างภาพด้วย Bing Image Creator

1. เปิด **https://www.bing.com/images/create**
2. วาง prompt ที่แต่งไว้ในช่อง
3. กด **Create** (หรือ Enter)
4. รอ 10-30 วินาที จะได้ภาพ 4 แบบ
5. เลือกภาพที่ชอบที่สุด → คลิก → **Download**

> **ถ้าไม่ถูกใจ:** เพิ่มคำเช่น `dramatic lighting`, `geometric shapes`, `abstract business concept` ใน prompt แล้วลองใหม่

---

### Step 3 — ใส่ตัวหนังสือใน Canva

1. เปิด **https://www.canva.com**
2. คลิก **Create a design** → พิมพ์ `Blog Banner` หรือ Custom Size **1200 × 628**
3. Upload ภาพที่ได้จาก Bing → ลาก set as background
4. เพิ่ม Text:
   - **ชื่อบทความ** (ไทย) — Font: Sarabun Bold, สีขาว หรือ Gold `#c9a96e`
   - **AIBiz Thailand** (เล็กๆ มุมล่างขวา) — สี Gold
5. **Download** → เลือก JPG, Quality 80%

**ตัวอย่าง Layout:**

```
┌─────────────────────────────────────┐
│                                     │
│   [ภาพ AI Background]               │
│                                     │
│   ชื่อบทความภาษาไทย                 │
│   (ตัวใหญ่ กลางภาพ หรือซ้ายล่าง)   │
│                              AIBiz  │
└─────────────────────────────────────┘
```

---

### Step 4 — Upload ขึ้น Django Admin

1. เปิด **http://localhost:8000/admin/blog/article/**
2. คลิก article ที่ต้องการ
3. หา field **Cover Image** → Upload ไฟล์ที่ได้
4. Save

---

## Tips

- **ภาพ Dark + Gold** เข้ากับ brand ของ AIBiz Thailand มากที่สุด
- **ไม่ต้องใส่ตัวหนังสือในภาพเสมอ** — บางบทความใช้ภาพสวยๆ โดยไม่มี text ก็ดูดี
- ถ้า Bing หมด credit ใช้ **https://ideogram.ai** แทนได้ (ดีเรื่องใส่ text ในภาพ)
- **Canva Template ที่แนะนำ:** ค้นหา "Blog Banner Dark" ใน Canva มีหลายแบบให้ใช้ฟรี

---

## Prompt สำเร็จรูปแยกตามหมวด

### หมวด Fear-based (บทความกลัวแพ้คู่แข่ง)

```
Professional Thai business blog cover. 
Two paths: one bright with AI technology, one dark without. 
Dark navy background, gold light rays, dramatic contrast.
Modern corporate style. No text. 16:9.
```

### หมวด AI News (ข่าว AI ล่าสุด)

```
Futuristic AI technology news blog cover.
Dark navy blue (#0f1b35) background, glowing circuit patterns.
Gold and white light elements, clean minimal design.
Professional tech journalism style. No text. 16:9.
```

### หมวด How-to / Tutorial

```
Professional tutorial guide blog cover for Thai SME business.
Step-by-step concept, dark navy background.
Gold progress elements, clean modern design.
Business education style. No text. 16:9.
```

---

*อัปเดต: พ.ค. 2569 | จัดทำโดย Chief of Staff*
