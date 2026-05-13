---
title: "วิธีใช้ Claude Code สำหรับมือใหม่: เริ่มต้นใน 10 นาที"
slug: how-to-use-claude-code-beginner
category: Educational
tags: ["Claude Code", "AI Coding", "Tutorial", "มือใหม่", "Anthropic"]
excerpt: "สอนใช้ Claude Code AI coding assistant ตั้งแต่ติดตั้งจนใช้งานได้จริง พร้อมตัวอย่างเขียนโค้ด แก้ bug และ automation สำหรับ dev ไทยมือใหม่ — เริ่มฟรี!"
meta_title: "วิธีใช้ Claude Code สำหรับมือใหม่: เริ่มต้นใน 10 นาที"
meta_description: "สอนใช้ Claude Code AI coding assistant ตั้งแต่ติดตั้งจนใช้งานได้จริง พร้อมตัวอย่างเขียนโค้ด แก้ bug และ automation สำหรับ dev ไทยมือใหม่ — เริ่มฟรี!"
cover_image_suggestion: "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=1200" # developer coding on laptop
status: draft
author_username: admin
word_count_target: 2000
reading_time_target: 10 min
---

# วิธีใช้ Claude Code สำหรับมือใหม่: เริ่มต้นใน 10 นาที

> **เคยเสียเวลาทั้งบ่ายแก้ bug ตัวเดียวไหม?** 😩
>
> เขียนโค้ดติดตรงไหนก็ค้นใน Stack Overflow ทีละหน้า อ่าน docs ภาษาอังกฤษไม่เข้าใจ ถามใน LINE กลุ่มก็เงียบ — ปัญหานี้นัก dev ไทยทุกคนน่าจะเจอ
>
> ถ้าเราบอกคุณว่ามี**เครื่องมือฟรีที่ช่วยให้คุณเขียนโค้ดเร็วขึ้นมาก** เข้าใจ codebase ของคุณ และตอบเป็นภาษาไทยได้ — คุณจะเชื่อไหม?
>
> เครื่องมือนั้นชื่อ **Claude Code** บทความนี้จะสอนคุณตั้งแต่ติดตั้งจนใช้งานได้จริงใน **10 นาที**

<div class="infographic">
  <div class="infographic-title">สรุป Claude Code ใน 1 ภาพ</div>
  <div class="infographic-grid">
    <div class="info-stat">
      <div class="stat-number">10 นาที</div>
      <div class="stat-label">เริ่มต้นใช้งาน</div>
    </div>
    <div class="info-stat">
      <div class="stat-number">ฟรี</div>
      <div class="stat-label">มี Free tier</div>
    </div>
    <div class="info-stat">
      <div class="stat-number">CLI</div>
      <div class="stat-label">ใช้ใน terminal</div>
    </div>
    <div class="info-stat">
      <div class="stat-number">TH ✓</div>
      <div class="stat-label">เข้าใจไทย</div>
    </div>
  </div>
</div>

---

## Claude Code คืออะไร?

**Claude Code** คือ AI coding assistant อย่างเป็นทางการจาก [Anthropic](https://anthropic.com) (บริษัทเดียวกับที่สร้าง Claude AI ที่หลายคนใช้ผ่านเว็บ)

แต่ Claude Code ไม่ใช่แค่ chatbot ตอบคำถาม — มันคือ **CLI tool ที่รันใน terminal ของคุณ** สามารถ:

- **อ่าน codebase ทั้ง project** ของคุณได้ ไม่ใช่แค่ snippet ที่ copy ไปวาง
- **แก้ไขไฟล์จริง** บนเครื่องคุณ ไม่ใช่แค่บอกว่าควรเขียนยังไง
- **รันคำสั่ง shell** ได้ (เช่น `npm install`, `git commit`)
- **เข้าใจภาษาไทย** ทั้ง prompt และ comment

ลองเปรียบเทียบให้เห็นภาพ:

| | ChatGPT | Claude Code |
|---|---------|-------------|
| รูปแบบ | เว็บ chat | CLI ใน terminal |
| เห็นไฟล์คุณไหม | ❌ ต้อง copy-paste | ✅ อ่านได้ทั้ง project |
| แก้ไฟล์ให้ได้ไหม | ❌ บอกว่าต้องแก้ | ✅ แก้ให้เลย |
| รันคำสั่งได้ไหม | ❌ | ✅ |
| ภาษาไทย | ✅ | ✅ |

---

## ทำไม Dev มือใหม่ควรใช้ Claude Code

ถ้าคุณเพิ่งเริ่มเขียนโค้ด หรือเป็น dev มาไม่นาน Claude Code จะเปลี่ยนวิธีทำงานของคุณ 3 ด้านหลัก:

**1. ประหยัดเวลาค้นหาคำตอบ**
แทนที่จะค้น "javascript array filter syntax" แล้วเปิด 5 แท็บเปรียบเทียบ — แค่บอก Claude Code ว่า "ช่วยเขียน function กรอง user ที่อายุเกิน 18" แล้วได้โค้ดพร้อมใช้ในไม่กี่วินาที

**2. อธิบายโค้ดเป็นภาษาไทยได้**
เจอโค้ดเก่าที่อ่านไม่ออก? พิมพ์ "อธิบายไฟล์นี้ให้ฟังเป็นภาษาไทย" Claude Code จะวิเคราะห์ไฟล์ทั้งหมดแล้วเล่าให้ฟังเหมือนพี่ในออฟฟิศสอนน้องใหม่

**3. ฟรี tier ใช้ได้พอสมควร**
ไม่ต้องจ่ายเงินก่อน — ลองใช้ฟรีก่อนตัดสินใจอัพเกรด

---

<div class="infographic">
  <div class="infographic-title">ติดตั้ง Claude Code ใน 5 ขั้นตอน</div>
  <div class="info-steps">
    <div class="info-step">
      <div class="step-num">1</div>
      <div class="step-text"><strong>สมัคร Anthropic Account</strong> — ที่ console.anthropic.com (ฟรี)</div>
    </div>
    <div class="info-step">
      <div class="step-num">2</div>
      <div class="step-text"><strong>Install ผ่าน npm</strong> — รัน <code>npm install -g @anthropic-ai/claude-code</code></div>
    </div>
    <div class="info-step">
      <div class="step-num">3</div>
      <div class="step-text"><strong>Authenticate</strong> — รัน <code>claude</code> แล้วทำตามขั้นตอน</div>
    </div>
    <div class="info-step">
      <div class="step-num">4</div>
      <div class="step-text"><strong>ทดสอบด้วย /help</strong> — ดูคำสั่งทั้งหมดที่ใช้ได้</div>
    </div>
    <div class="info-step">
      <div class="step-num">5</div>
      <div class="step-text"><strong>ลองใช้กับ project แรก</strong> — พิมพ์เป็นภาษาไทยได้เลย</div>
    </div>
  </div>
</div>

## ติดตั้ง Claude Code ใน 5 Step

> ⚠️ **ก่อนเริ่ม:** คุณต้องมี Node.js (เวอร์ชัน 18 ขึ้นไป) ติดตั้งบนเครื่อง — ถ้ายังไม่มี ดาวน์โหลดที่ [nodejs.org](https://nodejs.org)

### Step 1 — สมัคร Anthropic Account

ไปที่ [console.anthropic.com](https://console.anthropic.com) แล้วสมัครด้วย email หรือ Google

> 💡 **ถ้าอยากใช้ฟรี:** สมัคร Claude Free ที่ [claude.ai](https://claude.ai) แทน — Claude Code รองรับการ login ผ่าน Claude account ได้

### Step 2 — ติดตั้งผ่าน npm

เปิด terminal (ถ้า Windows ใช้ PowerShell หรือ Command Prompt) แล้วรันคำสั่ง:

```bash
npm install -g @anthropic-ai/claude-code
```

รอจนเสร็จ (ประมาณ 30 วินาที — 2 นาที ขึ้นกับความเร็วเน็ต)

### Step 3 — Authenticate ครั้งแรก

`cd` เข้าไปใน folder project ของคุณ (หรือสร้าง folder ใหม่ก็ได้) แล้วรัน:

```bash
claude
```

ครั้งแรกจะให้เลือกวิธี login:

- **Claude Pro/Max subscription** — ใช้ subscription ที่มีอยู่แล้ว (แนะนำสำหรับมือใหม่)
- **Anthropic API key** — สำหรับคนที่ใช้ API อยู่แล้ว

เลือกวิธีที่สะดวก แล้วทำตาม instruction ที่ขึ้นบนจอ

### Step 4 — ทดสอบด้วย /help

หลัง login สำเร็จจะเห็น prompt `>` รออยู่ ลองพิมพ์:

```
/help
```

จะขึ้นรายการคำสั่งที่ใช้ได้ทั้งหมด ถ้าเห็นแล้วแปลว่า **install สำเร็จ** 🎉

### Step 5 — ลองใช้กับ project แรก

ลองพิมพ์เป็นภาษาไทยเลย:

```
ช่วยอธิบายโครงสร้าง project นี้ให้ฟังหน่อย
```

Claude Code จะอ่านไฟล์ทั้ง folder แล้วเล่าให้ฟังว่ามีอะไรบ้าง — **ยินดีด้วย คุณใช้เป็นแล้ว!**

---

## ตัวอย่างใช้งานจริง 3 แบบ (ที่นัก dev มือใหม่ใช้บ่อย)

### ตัวอย่าง 1 — แก้ bug ที่ติดมา 2 ชม. ใน 30 วินาที

สมมุติว่าคุณเขียนโค้ด JavaScript แล้วเจอ error:

```
TypeError: Cannot read properties of undefined (reading 'map')
```

แทนที่จะ Google คุณแค่พิมพ์ใน Claude Code:

```
ใน file app.js เจอ error "Cannot read properties of undefined" ตอน render list ช่วยหาว่าทำไม + แก้ให้หน่อย
```

Claude Code จะ:
1. เปิดไฟล์ `app.js` อ่านโค้ด
2. หา root cause (เช่น state ยังไม่มีค่าตอน render ครั้งแรก)
3. แก้ไฟล์ให้คุณเลย พร้อมอธิบายว่าแก้อะไร

### ตัวอย่าง 2 — เขียน function ใหม่จาก spec

คุณอยากได้ function แต่ไม่อยากเขียนเอง:

```
ช่วยเขียน function ที่รับวันที่แบบ "2026-05-09" แล้วคืนค่าเป็นภาษาไทยแบบ "9 พฤษภาคม 2569"
```

Claude Code จะเขียนโค้ด, สร้างไฟล์ใหม่ (ถ้าจำเป็น), และ **เขียน test ให้ด้วย** ถ้าคุณขอ

### ตัวอย่าง 3 — Refactor โค้ดเก่าให้สะอาด

เจอไฟล์เก่ารกๆ ที่คนอื่นเขียนไว้?

```
ไฟล์ utils.js อ่านยากมาก ช่วย refactor ให้สะอาดขึ้น แต่ห้ามเปลี่ยน behavior นะ
```

Claude Code จะ refactor + รัน test (ถ้ามี) เพื่อ verify ว่า behavior ไม่เปลี่ยน

---

## 5 คำสั่งพื้นฐานที่ต้องรู้

ใน Claude Code มี **slash commands** ที่ขึ้นต้นด้วย `/` — นี่คือ 5 ตัวที่มือใหม่ใช้บ่อยที่สุด:

**1. `/help`**
แสดงรายการคำสั่งทั้งหมด — เปิดดูได้ตลอด ไม่ต้องจำ

**2. `/clear`**
ล้าง conversation ปัจจุบัน เริ่มใหม่ — ใช้เมื่อจะเปลี่ยน topic

**3. `/init`**
ให้ Claude Code อ่าน project ทั้งหมดแล้วสร้าง `CLAUDE.md` (ไฟล์อธิบายโปรเจกต์) — **รันครั้งเดียวตอน setup project ใหม่**

**4. `/agents`**
ดูรายการ subagents ที่มี — agents คือ AI ผู้เชี่ยวชาญเฉพาะด้านที่คุณสร้างได้เอง (advanced)

**5. `/model`**
เปลี่ยนรุ่น AI ที่ใช้ — เช่น เปลี่ยนเป็น Haiku (เร็ว ถูก) หรือ Opus (ฉลาดสุด ช้ากว่า)

> 💡 **Pro tip:** พิมพ์ `/` แล้ว Claude Code จะแสดง autocomplete ของทุกคำสั่ง — ไม่ต้องจำ

---

## ข้อควรระวัง + คำถามที่พบบ่อย (FAQ)

### Claude Code ใช้ฟรีไหม?

**ใช่ — มี free tier** ถ้าคุณมี Claude Free account สามารถใช้งานได้แต่มี usage limit
ถ้าใช้เยอะขึ้นแนะนำ Claude Pro ($20/เดือน) จะใช้ได้สบายกว่า
สำหรับ business ที่ใช้หนักให้ดู Claude Max หรือใช้ผ่าน Anthropic API

### Windows install ติดอะไรบ่อย?

ปัญหาที่เจอบ่อยที่สุดคือ **Node.js เก่า** — ตรวจด้วย `node --version` ต้อง ≥ 18
ถ้าติด permission error ลองรัน PowerShell แบบ "Run as Administrator"

### Claude Code ต่างจาก Cursor/Copilot ยังไง?

| | Claude Code | Cursor | Copilot |
|---|-------------|--------|---------|
| รูปแบบ | CLI | IDE (fork ของ VS Code) | VS Code extension |
| ฟรี | มี free tier | มี free tier limit | ไม่มี (จ่ายอย่างเดียว) |
| รันคำสั่งได้ | ✅ | ⚠️ จำกัด | ❌ |
| เหมาะกับ | งาน automation, deep work | UI-first dev | autocomplete |

แต่ละตัวมีจุดเด่นต่างกัน — **ใช้คู่กันได้** หลายคนใช้ Cursor เป็น IDE + Claude Code สำหรับงาน automation

### Claude Code ใช้กับ VS Code ได้ไหม?

ได้ มี **VS Code extension** อย่างเป็นทางการ (ค้นใน Marketplace ว่า "Claude Code")
หลังติดตั้ง เปิด terminal ใน VS Code แล้ว `claude` เข้าได้เลย — extension จะ enhance UX เพิ่มเติม

### ภาษาไทย support ดีแค่ไหน?

**ดีมาก** — Claude เข้าใจไทยทั้ง prompt, comment, และ string ในโค้ด
แต่แนะนำให้ใช้ **prompt ภาษาอังกฤษสำหรับชื่อ function** (เพราะ codebase ส่วนใหญ่เป็น English) แต่ explain/discuss เป็นไทยได้สบาย

---

<div class="infographic">
  <div class="infographic-title">5 คำสั่งพื้นฐานที่ต้องรู้</div>
  <div class="info-steps">
    <div class="info-step">
      <div class="step-num">/h</div>
      <div class="step-text"><strong>/help</strong> — ดูคำสั่งทั้งหมด เปิดได้ตลอด ไม่ต้องจำ</div>
    </div>
    <div class="info-step">
      <div class="step-num">/c</div>
      <div class="step-text"><strong>/clear</strong> — ล้าง conversation เริ่มใหม่</div>
    </div>
    <div class="info-step">
      <div class="step-num">/i</div>
      <div class="step-text"><strong>/init</strong> — สร้าง CLAUDE.md ให้ Claude อ่าน project (รันครั้งเดียว)</div>
    </div>
    <div class="info-step">
      <div class="step-num">/a</div>
      <div class="step-text"><strong>/agents</strong> — ดู subagents ที่มี (advanced)</div>
    </div>
    <div class="info-step">
      <div class="step-num">/m</div>
      <div class="step-text"><strong>/model</strong> — เปลี่ยนรุ่น AI (Haiku เร็ว / Opus ฉลาด)</div>
    </div>
  </div>
</div>

## ขั้นต่อไปสำหรับคนที่อยากใช้เก่งขึ้น

ตอนนี้คุณติดตั้งและใช้งานพื้นฐานเป็นแล้ว ขั้นต่อไปแนะนำ:

📚 **อ่านบทความถัดไป:**
- *[เร็ว ๆ นี้]* "10 Slash Commands ที่ทำให้ Claude Code เร็วขึ้น 5 เท่า"
- *[เร็ว ๆ นี้]* "สอนใช้ Hooks ใน Claude Code ทำ automation"

🎯 **ลองสร้าง custom subagent** สำหรับงานเฉพาะของคุณ (เช่น "agent ตรวจ security ของโค้ด PHP")

🛠️ **เชื่อมกับ MCP server** เพื่อให้ Claude Code เข้าถึง Slack, Google Drive, database ได้

---

## 💡 อยากเอา AI มาใช้ในธุรกิจหรือทีม dev คุณ?

Claude Code คือเครื่องมือที่ดีสำหรับ dev เดี่ยว — แต่ถ้าคุณมีทีม หรือมีธุรกิจที่อยากใช้ AI workflow แบบเต็มระบบ (chatbot, automation, lead generation) — เราช่วยได้

ทีมเราเชี่ยวชาญด้าน **AI Automation สำหรับ SME ไทย** ตั้งแต่ออกแบบระบบ chatbot, สร้าง custom AI agent, ไปจนถึงเชื่อม AI กับ workflow ภายในองค์กร

🎁 **ขอ AI Audit ฟรี 30 นาที** — ทีมเราจะวิเคราะห์ workflow ของคุณแล้วบอกว่าจุดไหน AI ช่วยได้คุ้มที่สุด ไม่มีค่าใช้จ่าย ไม่มีการขายตรง

👉 **[จองเวลา AI Audit ฟรี →](/contact/)**

---

*บทความนี้อ้างอิงจาก [Claude Code Documentation อย่างเป็นทางการ](https://code.claude.com/docs/) อัพเดต ณ พฤษภาคม 2026 — ฟีเจอร์อาจมีการเปลี่ยนแปลง โปรดตรวจ docs ทางการก่อนใช้งานจริง*
