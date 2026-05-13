# Content Backlog — Queue ของบทความที่จะเขียน

> 📌 **วิธีใช้:**
> - **พี่:** เพิ่ม topic ใหม่ลงตาราง "Queue" ด้านล่าง (priority + notes ก็ใส่ได้)
> - **หนูดี:** หยิบจาก queue ตามลำดับ priority → ทำ Workflow E ครบทุก stage → ย้ายลง "Done"
> - **กฎ:** หนูดีจะ **ไม่ publish เอง** — ทำ draft แล้ว stop ที่ Stage 8 (publish เป็น `status=draft` ใน Django) ให้พี่กด publish เอง

---

## 🚀 วิธีให้หนูดีเริ่มทำงาน

พิมพ์อย่างใดอย่างหนึ่ง:

| คำสั่ง | ทำอะไร |
|--------|--------|
| `หนูดี - process backlog` | หยิบ topic ลำดับสูงสุดที่ status `pending` มาทำ 1 ตัว |
| `หนูดี - process backlog ทั้งหมด` | ทำทุก topic ที่ pending จนหมด queue |
| `หนูดี - process "ชื่อ topic"` | เลือก topic ที่ต้องการให้ทำก่อน |
| `หนูดี - แสดง backlog` | สรุปสถานะทั้งหมด |

---

## 📝 Queue (เพิ่ม topic ใหม่ที่นี่)

| # | Status | Priority | Topic | Target Keyword | Notes | Added | Owner |
|---|--------|----------|-------|----------------|-------|-------|-------|
| 1 | `done` | 🔴 High | วิธีใช้ Claude Code สำหรับมือใหม่ | วิธีใช้ claude code | First test article | 2026-05-09 | All |
| 2 | `pending` | — | _เพิ่ม topic ของพี่ที่นี่_ | — | — | — | — |

---

## 🎯 Status Values
- `pending` — ยังไม่เริ่ม รอหนูดีหยิบ
- `in-progress` — หนูดีกำลังทำอยู่ (Stage X/9)
- `review` — เสร็จแล้ว รอพี่ตรวจ + publish
- `done` — Publish แล้ว ย้ายลงตาราง Done

## 🚦 Priority
- 🔴 **High** — รีบ, ทำก่อน
- 🟡 **Medium** — ตามคิว
- 🟢 **Low** — เมื่อว่าง / batch รวมกับตัวอื่น

---

## 📋 Template สำหรับเพิ่ม Topic ใหม่

Copy แล้ววางในตาราง Queue ด้านบน:

```
| N | pending | 🟡 Medium | <ชื่อบทความ> | <keyword หลัก> | <โน้ตเพิ่มเติม> | YYYY-MM-DD | — |
```

ตัวอย่างที่ดี:
```
| 3 | pending | 🔴 High | สอนใช้ Slash Command ใน Claude Code | claude code slash command | เน้น 10 คำสั่งที่ใช้บ่อย + ตัวอย่าง | 2026-05-10 | — |
| 4 | pending | 🟡 Medium | Hooks ทำ automation ยังไง | claude code hooks | follow-up จากบทความ slash command | 2026-05-10 | — |
| 5 | pending | 🟢 Low | Claude Code vs Cursor vs Copilot | claude code vs cursor | ทำเป็น comparison ยาว 3,000 คำ | 2026-05-10 | — |
```

---

## ✅ Done (Archive)

| # | Topic | Slug | Published | Notes |
|---|-------|------|-----------|-------|
| 1 | วิธีใช้ Claude Code สำหรับมือใหม่ | how-to-use-claude-code-beginner | 2026-05-09 (draft) | First end-to-end test |

---

## 📁 ไฟล์ที่เกี่ยวข้อง

- `content_backlog/drafts/` — draft markdown ระหว่างทำ (Stage 4-7)
- `content_backlog/done/` — archive ของ draft ที่ publish แล้ว
- `content_briefs/` — keyword brief จาก SEO Specialist
- `workflows/workflow_e_content_pipeline.md` — workflow ทั้ง 9 stages
