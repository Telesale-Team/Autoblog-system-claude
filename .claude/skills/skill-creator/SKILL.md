---
name: skill-creator
description: Meta-skill that scaffolds a new Claude Code skill with proper frontmatter, structure, and registration. Use whenever the user asks to create a new skill, add a reusable capability, or wrap a repeatable workflow into a skill. Ensures every skill follows the project's standard template and is registered in CLAUDE.md.
---

# Skill: Skill Creator

สร้าง skill ใหม่แบบมีมาตรฐาน — ไม่ต้องจำ format เอง

## เมื่อไหร่ใช้
- ผู้ใช้ขอสร้าง skill ใหม่
- พบ workflow ที่ทำซ้ำๆ ควรห่อเป็น skill
- ต้องการ wrap external API หรือ tool เข้ามาเป็น skill ที่เรียกง่าย

## Input ที่ต้องถามผู้ใช้ (ถ้ายังไม่ได้บอก)
1. **ชื่อ skill** (kebab-case, ภาษาอังกฤษ) เช่น `linkedin-post-publisher`
2. **จุดประสงค์ 1 ประโยค** — ทำอะไร ใช้ตอนไหน
3. **Input ที่ต้องการ** — รับอะไรมา
4. **Output ที่ส่งกลับ** — ส่งอะไรออก
5. **Tool dependencies** — ใช้ Bash/WebFetch/Edit/external API อะไรบ้าง
6. **Owner agent** — agent ตัวไหนเป็นคนเรียกใช้หลัก

## ขั้นตอนการสร้าง

### Step 1: Validate ชื่อ skill
- ต้องเป็น kebab-case: `[a-z0-9-]+`
- ต้องไม่ซ้ำกับ skill ที่มี (เช็คใน `.claude/skills/`)
- สั้น กระชับ บอกหน้าที่ได้ในตัว

### Step 2: เขียน description ให้ดี (สำคัญมาก!)
Description คือสิ่งที่ Claude ใช้ตัดสินใจว่าจะเรียก skill นี้ตอนไหน
**Template:**
```
[Verb-action ที่ skill ทำ] for [domain/purpose]. Use when [trigger condition 1], [trigger condition 2], or [trigger condition 3].
```
ตัวอย่างดี:
- ✅ "Scrape and structure documentation from code.claude.com/docs into clean markdown for Thai content creation. Use when Content Writer needs source material from official Claude Code documentation."

ตัวอย่างไม่ดี:
- ❌ "Helps with docs" (สั้น/คลุมเครือ)
- ❌ "This skill scrapes things" (ไม่บอก trigger)

### Step 3: สร้าง folder + SKILL.md
```bash
mkdir -p ".claude/skills/<skill-name>"
```

ใช้ template นี้ในการเขียน `SKILL.md`:

````markdown
---
name: <skill-name>
description: <description per template above>
---

# Skill: <Title Case Name>

<1-2 ประโยคบอกว่า skill นี้ทำอะไร>

## เมื่อไหร่ใช้
- <use case 1>
- <use case 2>
- <use case 3>

## Prerequisites (ถ้ามี)
- <สิ่งที่ต้องเตรียมก่อน>

## Input ที่ต้องการ
```yaml
field1: ...
field2: ...
```

## ขั้นตอน

### Step 1: <ชื่อ step>
<รายละเอียด + tool calls ตัวอย่าง>

### Step 2: <ชื่อ step>
...

### Step N: ส่งกลับ output
<format ของ output>

## Output ที่ส่งกลับ
- <รายการ output>

## Anti-pattern (ห้ามทำ)
- ❌ <สิ่งที่ห้ามทำ + เหตุผล>
- ❌ ...

## Owner Agent
- Primary: <agent slug>
- Supporting: <agent slugs>
````

### Step 4: ลงทะเบียนใน CLAUDE.md
แก้ตาราง skills ใน `CLAUDE.md` section "Skills (ใน `.claude/skills/`)":
```markdown
| `<skill-name>` | <ใช้เมื่อไหร่ — สั้นๆ 1 ประโยค> |
```

### Step 5: Verify
- [ ] Folder + SKILL.md สร้างสำเร็จ
- [ ] Frontmatter parse ได้ (name, description ครบ)
- [ ] CLAUDE.md อัพเดต
- [ ] Description บอก trigger conditions ชัดเจน

## Output ที่ส่งกลับ
- Path ของ skill ใหม่: `.claude/skills/<skill-name>/SKILL.md`
- คำสั่งเรียกใช้ตัวอย่าง
- Confirmation ว่า CLAUDE.md อัพเดตแล้ว

## Anti-pattern (ห้ามทำ)
- ❌ ตั้งชื่อ skill ภาษาไทย (Claude Code ไม่รับ)
- ❌ Description สั้นกว่า 20 คำ (Claude routing ไม่ได้)
- ❌ สร้าง skill ที่ทำงานเดียวกับ skill ที่มีอยู่แล้ว → update ของเดิมแทน
- ❌ ลืมลงทะเบียนใน CLAUDE.md → skill จะหายไปจาก index
- ❌ ใส่ secrets / API keys ในไฟล์ SKILL.md ตรงๆ → ใช้ environment variables

## Owner Agent
- Primary: `ai-toolsmith`
- Supporting: any agent ที่ต้องการ skill ใหม่
