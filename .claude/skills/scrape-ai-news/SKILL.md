---
name: scrape-ai-news
description: Search and fetch the latest AI news from major companies (Anthropic, OpenAI, Google DeepMind, Meta AI, xAI, Mistral) using WebSearch + WebFetch, then return structured briefs as JSON with Thai summaries and SME-relevance scoring. Use when AI News Scout needs to collect today's AI updates, when Content Writer TH needs source material for news articles, or when the news pipeline (Workflow F) is triggered.
---

# Skill: Scrape AI News

ดึงข่าวล่าสุดจากค่าย AI ชั้นนำ แล้ว return structured brief พร้อม summary ภาษาไทยและคะแนนความเกี่ยวข้องกับ SME ไทย

## เมื่อไหร่ใช้
- AI News Scout ต้องการข่าว AI วันนี้ก่อนเขียน brief
- Content Writer TH ต้องการ source material สำหรับบทความข่าว AI
- Workflow F (AI News Pipeline) ถูก trigger ทั้งแบบ manual และ scheduled

## Prerequisites
- WebSearch tool พร้อมใช้งาน
- WebFetch tool พร้อมใช้งาน
- ภาษาที่ใช้ใน summary_th ต้องเป็นภาษาไทยเป็นธรรมชาติ (ไม่ใช่ Google Translate)

## Input ที่ต้องการ
```yaml
sources:          # optional — ถ้าไม่ระบุ ใช้ default list
  - anthropic
  - openai
  - google-deepmind
  - meta-ai
  - xai
  - mistral
max_items: 5      # จำนวนข่าวสูงสุดที่ต้องการ (default: 5)
date_range: today # "today" | "this_week" | "last_7_days"
min_relevance: 6  # ตัด brief ที่ relevance_score ต่ำกว่านี้ออก (0-10)
```

## ขั้นตอน

### Step 1: WebSearch หาข่าวใน 2 กลุ่ม

#### กลุ่ม A — ข่าวจากค่าย AI ใหญ่ (AI Company News)
```
"Anthropic" AI news announcement site:anthropic.com OR site:techcrunch.com OR site:theverge.com 2026
"OpenAI" news release announcement 2026
"Google DeepMind" OR "Google AI" release update 2026
"Meta AI" Llama announcement 2026
"xAI" Grok announcement Elon Musk 2026
"Mistral AI" release update 2026
```

#### กลุ่ม B — ข่าว AI ประยุกต์ใช้แยกตาม Segment (Sector News)
```
AI hospital clinic healthcare Thailand 2026 automation
AI ecommerce Shopee Lazada LINE shopping Thailand 2026
AI hotel resort hospitality OTA booking Thailand 2026
AI spa beauty wellness salon appointment 2026
AI HR recruitment education school EdTech Thailand 2026
AI coach freelancer creator online course revenue 2026
```

เก็บ URL ของบทความที่น่าสนใจ (title บ่งบอกว่ามีการ release/launch/update หรือ use case จริง)

### Step 2: WebFetch เนื้อหาบทความ

สำหรับแต่ละ URL ที่ได้จาก Step 1:
- WebFetch ดึงเนื้อหาเต็ม
- อ่านเฉพาะ: headline, date, ย่อหน้าแรก 3-5 ย่อหน้า
- ถ้า WebFetch ไม่ได้ ใช้ description จาก search result แทน

### Step 3: สร้าง structured brief แต่ละข่าว

**หลักการเขียนสำหรับเจ้าของธุรกิจที่ไม่ชำนาญ AI:**
- ทุกคำศัพท์ภาษาอังกฤษหรือศัพท์เทคนิค **ต้องมีวงเล็บอธิบายความหมายภาษาไทย**
  - เช่น: API (ช่องทางเชื่อมต่อระบบ), LLM (AI ที่เข้าใจและสร้างภาษา), Fine-tuning (การสอน AI เพิ่มเติม)
- ใช้การเปรียบเทียบกับสิ่งที่คุ้นเคย เช่น "เหมือนจ้างพนักงานอัตโนมัติ"
- เน้นผลกระทบต่อธุรกิจจริง ไม่ใช่เทคโนโลยี

```json
{
  "headline": "ชื่อข่าวภาษาอังกฤษต้นฉบับ",
  "source": "anthropic | openai | google-deepmind | meta-ai | xai | mistral | sector",
  "source_url": "https://...",
  "published_date": "YYYY-MM-DD",
  "news_group": "company | sector",
  "target_segment": "general | healthcare | ecommerce | hospitality | beauty | hr-education | creator-coach",
  "target_writer": "content-writer-th | healthcare-content-writer | ecommerce-content-writer | hospitality-content-writer | beauty-wellness-writer | hr-education-writer | creator-coach-writer",
  "summary_en": "2-3 sentences summary in English",
  "summary_th": "2-3 ประโยคสรุปภาษาไทยแบบธรรมชาติ สำหรับเจ้าของธุรกิจที่ไม่รู้จัก AI — ไม่ใช้ศัพท์เทคนิคโดยไม่อธิบาย",
  "plain_th": "อธิบายข่าวนี้ในภาษาที่แม่ค้าตลาดหรือเจ้าของร้านอาหารทั่วไปเข้าใจได้ทันที ใช้การเปรียบเทียบกับชีวิตประจำวัน 3-4 ประโยค",
  "glossary": [
    {"term": "คำศัพท์ภาษาอังกฤษหรือเทคนิค", "meaning": "คำอธิบายง่ายๆ ภาษาไทย 1 ประโยค"}
  ],
  "sme_impact": "ธุรกิจ SME ไทยจะได้รับผลกระทบอะไร อธิบายเป็นรูปธรรม เช่น ประหยัดเงินเท่าไหร่ ลดขั้นตอนอะไร",
  "key_points": ["จุดสำคัญ 1 (ภาษาไทยเข้าใจง่าย)", "จุดสำคัญ 2", "จุดสำคัญ 3"],
  "relevance_score": 8,
  "relevance_reason": "เหตุผลว่าทำไมถึงเกี่ยวกับ SME ไทย",
  "suggested_angle_th": "มุมที่แนะนำสำหรับเขียนบทความภาษาไทย เช่น 'SME ไทยจะได้ประโยชน์อย่างไร'"
}
```

#### Segment Routing Table

| เนื้อหาข่าว | target_segment | target_writer |
|------------|---------------|---------------|
| AI จากค่ายใหญ่, automation ทั่วไป | general | content-writer-th |
| คลินิก, โรงพยาบาล, PDPA, เวชระเบียน | healthcare | healthcare-content-writer |
| Shopee, Lazada, LINE, ร้านค้าออนไลน์ | ecommerce | ecommerce-content-writer |
| โรงแรม, รีสอร์ท, OTA, ท่องเที่ยว | hospitality | hospitality-content-writer |
| ร้านนวด, สปา, คลินิกความงาม | beauty | beauty-wellness-writer |
| HR, สรรหาคน, โรงเรียน, EdTech | hr-education | hr-education-writer |
| โค้ช, Freelancer, คอร์สออนไลน์ | creator-coach | creator-coach-writer |

**Relevance Score (0-10) สำหรับ SME ไทย:**
- 9-10: เปลี่ยนเกมชัดเจน เช่น AI ราคาถูกลงมาก, API ใหม่ที่ไม่ต้องเขียน code
- 7-8: มีประโยชน์โดยตรง เช่น tool ใหม่, feature ที่ automation ได้ง่ายขึ้น
- 5-6: น่าสนใจแต่ indirect เช่น model ใหม่ที่ยังไม่ release
- 1-4: เป็นข่าว research/academic ที่ยังไกล SME
- ตัดทิ้ง: ข่าวพนักงาน, lawsuit, drama

### Step 4: เรียง + filter

- เรียงตาม `relevance_score` จากมากไปน้อย
- ตัดข่าวที่ `relevance_score < min_relevance` ออก
- จำกัดที่ `max_items` ข่าว
- ถ้า 2 ข่าวจากค่ายเดียวกัน เลือกอันที่ score สูงกว่า (diversity)

### Step 5: บันทึก ContentBacklog + CalendarEvent ลง DB

**สำคัญมาก:** ทุกข่าวที่ผ่าน filter ต้องบันทึกลง DB ทันที ก่อน return output

สำหรับแต่ละ brief ใน briefs[] ให้รัน management command ต่อไปนี้:

```powershell
# 1. สร้าง ContentBacklog entry
.\venv\Scripts\python.exe manage.py shell -c "
import sys; sys.stdout.reconfigure(encoding='utf-8')
from marketing.models import ContentBacklog
from dashboard.models import CalendarEvent
from django.utils import timezone

topic = '<suggested_angle_th หรือ headline ภาษาไทย>'
keyword = '<keyword หลักจาก brief>'
notes = '<summary_th> | Source: <source_url> | SME Impact: <sme_impact>'

# ป้องกัน duplicate — ตรวจก่อนสร้าง
if not ContentBacklog.objects.filter(topic=topic).exists():
    backlog = ContentBacklog.objects.create(
        topic=topic,
        keyword=keyword,
        priority='P1',
        status='pending',
        notes=notes,
        owner='<target_writer>',
        added_by='ยูโร (AI News Scout)',
    )
    # สร้าง CalendarEvent พร้อมกัน
    event = CalendarEvent.objects.create(
        title=topic,
        category='article',
        is_system=True,
        start_datetime=timezone.now(),
        all_day=True,
        is_completed=False,
        description='ข่าว AI รอเขียน: ' + topic,
        created_by=None,
    )
    # Link backlog → event
    backlog.calendar_event = event
    backlog.save(update_fields=['calendar_event'])
    print(f'Created: backlog={backlog.pk} event={event.pk}')
else:
    print(f'Skip duplicate: {topic[:50]}')
"
```

**กฎ:** ห้ามใส่ `[ข่าว AI]` prefix ใน title ของ CalendarEvent — ใช้ `suggested_angle_th` เป็น title โดยตรง

### Step 6: ส่งกลับ output

```json
{
  "fetched_at": "2026-05-17T10:00:00+07:00",
  "total_found": 12,
  "total_selected": 5,
  "briefs": [ ...array of brief objects... ],
  "saved_to_db": 5,
  "next_action": "ข่าวทั้งหมดบันทึกลง ContentBacklog และ CalendarEvent แล้ว รอ user อนุมัติที่ /owner/backlog/"
}
```

## Output ที่ส่งกลับ
- JSON object ตาม format ด้านบน
- `briefs[]` เรียงตาม relevance_score DESC
- `saved_to_db` = จำนวน record ที่บันทึกจริง (ไม่นับ duplicate ที่ skip)
- แต่ละ brief มี `suggested_angle_th` พร้อมส่งต่อ Content Writer TH ได้เลย

## Anti-pattern (ห้ามทำ)
- ❌ ดึงข่าวจาก Twitter/X เป็นหลัก — ข้อมูลไม่ verified, ใช้เฉพาะ official blog + tech press
- ❌ แปล summary_th แบบ word-for-word — เขียนใหม่ด้วยภาษาไทยธรรมชาติ
- ❌ ให้ relevance_score สูงกับข่าว research paper ที่ยังไม่มีผลิตภัณฑ์จริง
- ❌ ส่งข่าวซ้ำจากค่ายเดียวกันเกิน 1 ข่าว (ยกเว้น score ต่างกันมาก)
- ❌ ข้ามขั้นตอน WebFetch — summary จาก search snippet อาจผิดพลาด

## ❌ ห้ามใช้ศัพท์เหล่านี้โดยไม่อธิบาย (ต้องมีวงเล็บทุกครั้ง)

| ศัพท์เทคนิค | ต้องอธิบายว่า |
|------------|-------------|
| API | (ช่องทางเชื่อมต่อระบบ) |
| LLM | (AI ที่เข้าใจและสร้างภาษา) |
| Model / AI Model | (สมอง/ตัวโปรแกรม AI) |
| Fine-tuning | (การสอน AI เพิ่มเติมให้รู้จักธุรกิจของเรา) |
| Inference | (การที่ AI ประมวลผลและตอบคำถาม) |
| Token | (หน่วยวัดความยาวข้อความของ AI) |
| Open source | (โปรแกรมให้ใช้ฟรี แก้ไขได้) |
| Multimodal | (AI ที่เข้าใจได้ทั้งข้อความ รูปภาพ และเสียง) |
| Agent | (AI ที่ทำงานอัตโนมัติได้หลายขั้นตอนเอง) |
| Prompt | (คำสั่งที่พิมพ์ให้ AI) |
| GPT / Claude / Gemini | (ชื่อโปรแกรม AI แต่ละยี่ห้อ) |
| Deployment | (การนำระบบไปใช้งานจริง) |
| Benchmark | (ผลการทดสอบวัดประสิทธิภาพ) |

## Owner Agent
- Primary: `ai-news-scout`
- Supporting: `content-writer-th`
