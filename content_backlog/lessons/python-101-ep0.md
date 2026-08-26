<!-- ต้นฉบับ Markdown ของ Article #43 — แก้ที่นี่หรือใน Django admin ก็ได้ -->
<!-- title: EP0: คอร์ส Python สำหรับคนเริ่มต้น — เขียนโปรแกรมให้ทำงานแทนเรา -->

ทุกสิ้นวันคุณเปิด Excel ขึ้นมานั่งบวกยอดขายทีละบิล ทุกสิ้นเดือนคุณก๊อปข้อมูลจากไฟล์หนึ่งไปวางอีกไฟล์หนึ่ง ทุกเช้าคุณเปิด 5 แท็บเพื่อเช็คตัวเลขเดิมๆ — งานพวกนี้กินเวลาวันละ 20 นาที ฟังดูน้อย แต่ปีหนึ่งคือ **120 ชั่วโมง** ที่หายไปกับงานที่คอมพิวเตอร์ทำแทนได้ทั้งหมด

คอร์สนี้ไม่ได้จะเปลี่ยนคุณเป็นโปรแกรมเมอร์ครับ แต่จะสอนให้คุณ**สั่งคอมพิวเตอร์ทำงานซ้ำๆ แทนคุณได้** ด้วยภาษา Python — ภาษาที่อ่านแล้วเกือบเหมือนภาษาอังกฤษธรรมดา และเป็นภาษาที่มือใหม่เริ่มได้ง่ายที่สุดในตอนนี้

:::analogy 🍳
การเขียนโปรแกรมก็เหมือน**เขียนสูตรอาหารให้คนที่ทำตามเป๊ะมาก แต่ไม่คิดเอง** ถ้าคุณเขียนว่า "ใส่เกลือ" เขาจะใส่ทั้งถุง เพราะคุณไม่ได้บอกว่ากี่ช้อน ทั้งคอร์สนี้คือการฝึกเขียนสูตรให้ชัดจนคอมพิวเตอร์ทำตามได้ถูก
:::

## คอร์สนี้เหมาะกับใคร

ผมเขียนคอร์สนี้โดยคิดถึงคน 3 กลุ่มนี้เป็นหลักครับ

:::step 1 เจ้าของธุรกิจ / คนทำงานออฟฟิศที่เบื่องานซ้ำ
คุณรู้ว่างานที่ทำอยู่มันน่าจะทำอัตโนมัติได้ แต่ไม่รู้จะเริ่มตรงไหน — เริ่มที่นี่ครับ
:::

:::step 2 คนที่เคยลองเรียนเขียนโค้ดแล้วเลิกกลางคัน
ส่วนใหญ่เลิกเพราะเรียนไป 3 บทแล้วยังไม่รู้ว่าจะเอาไปทำอะไร คอร์สนี้ทุกบทจบด้วยโปรแกรมที่ใช้ได้จริง 1 ตัว
:::

:::step 3 คนที่อยากคุยกับ AI ให้เขียนโค้ดให้รู้เรื่อง
ทุกวันนี้ AI เขียนโค้ดให้ได้ แต่ถ้าคุณอ่านโค้ดไม่ออกเลย คุณจะไม่รู้ว่ามันเขียนถูกหรือผิด คอร์สนี้ทำให้คุณ**ตรวจงาน AI เป็น**
:::

:::warn[⚠️] คอร์สนี้ไม่เหมาะกับใคร
ถ้าคุณเขียน Python เป็นอยู่แล้ว หรืออยากได้คอร์สที่ลงลึกเรื่อง Data Science / Machine Learning โดยตรง คอร์สนี้จะช้าเกินไปสำหรับคุณครับ — เริ่มที่ EP8 เป็นต้นไปแทน
:::

## จบคอร์สแล้วคุณจะทำอะไรได้

ปลายทางของคอร์สนี้ไม่ใช่ใบประกาศ แต่เป็น**โปรแกรมจริง 1 ตัวที่คุณเขียนเองและใช้ทุกวัน**

:::tip[🎯] ผลงานปลายคอร์ส (EP12)
โปรแกรมที่เปิดไฟล์ยอดขายของร้านคุณ → คำนวณยอดรวม สินค้าขายดี และเทียบกับเมื่อวาน → ส่งสรุปเข้า LINE ให้คุณทุกเย็นอัตโนมัติ โดยคุณไม่ต้องแตะอะไรเลย
:::

ระหว่างทางคุณจะได้โปรแกรมเล็กๆ อีก 11 ตัว ตั้งแต่เครื่องคิดเลขคิดกำไร ไปจนถึงโปรแกรมอ่านไฟล์ Excel ทุกตัวเก็บไว้ใช้ต่อได้จริง ไม่ใช่โค้ดฝึกหัดที่เขียนเสร็จแล้วทิ้ง

## แผนที่คอร์ส — 12 บทเรียน 3 ช่วง

:::figure เส้นทางเรียนทั้งหมด — แต่ละช่วงต่อยอดจากช่วงก่อนหน้า ห้ามข้าม
<svg viewBox="0 0 760 340" role="img" aria-label="แผนที่คอร์ส Python 12 บทเรียน แบ่งเป็น 3 ช่วง: พื้นฐาน จัดการข้อมูล และของจริง" xmlns="http://www.w3.org/2000/svg"><text x="20" y="26" font-family="Segoe UI,sans-serif" font-size="14" font-weight="700" fill="#f1f5f9">เส้นทางเรียน 12 บทเรียน</text><rect x="20" y="45" width="230" height="272" rx="14" fill="#0f1626" stroke="#1f2937"/><text x="36" y="72" font-family="Segoe UI,sans-serif" font-size="13.5" font-weight="700" fill="#c9a96e">ช่วงที่ 1 — พื้นฐาน</text><text x="36" y="90" font-family="Segoe UI,sans-serif" font-size="11" fill="#94a3b8">สั่งคอมพิวเตอร์ให้ทำตามได้</text><rect x="36" y="102" width="198" height="40" rx="9" fill="#111827" stroke="#1f2937"/><circle cx="60" cy="122" r="13" fill="rgba(201,169,110,0.12)" stroke="#c9a96e" stroke-opacity="0.55"/><text x="60" y="127" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="11" font-weight="700" fill="#c9a96e">1</text><text x="82" y="127" font-family="Segoe UI,sans-serif" font-size="12.5" fill="#cbd5e1">ติดตั้ง + รันโค้ดแรก</text><rect x="36" y="150" width="198" height="40" rx="9" fill="#111827" stroke="#1f2937"/><circle cx="60" cy="170" r="13" fill="rgba(201,169,110,0.12)" stroke="#c9a96e" stroke-opacity="0.55"/><text x="60" y="175" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="11" font-weight="700" fill="#c9a96e">2</text><text x="82" y="175" font-family="Segoe UI,sans-serif" font-size="12.5" fill="#cbd5e1">ตัวแปร + ชนิดข้อมูล</text><rect x="36" y="198" width="198" height="40" rx="9" fill="#111827" stroke="#1f2937"/><circle cx="60" cy="218" r="13" fill="rgba(201,169,110,0.12)" stroke="#c9a96e" stroke-opacity="0.55"/><text x="60" y="223" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="11" font-weight="700" fill="#c9a96e">3</text><text x="82" y="223" font-family="Segoe UI,sans-serif" font-size="12.5" fill="#cbd5e1">รับค่า + จัดข้อความ</text><rect x="36" y="246" width="198" height="40" rx="9" fill="#111827" stroke="#1f2937"/><circle cx="60" cy="266" r="13" fill="rgba(201,169,110,0.12)" stroke="#c9a96e" stroke-opacity="0.55"/><text x="60" y="271" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="11" font-weight="700" fill="#c9a96e">4</text><text x="82" y="271" font-family="Segoe UI,sans-serif" font-size="12.5" fill="#cbd5e1">เงื่อนไข if/else</text><polygon points="252,180 264,187 252,194" fill="#c9a96e" fill-opacity="0.7"/><rect x="265" y="45" width="230" height="272" rx="14" fill="#0f1626" stroke="#1f2937"/><text x="281" y="72" font-family="Segoe UI,sans-serif" font-size="13.5" font-weight="700" fill="#c9a96e">ช่วงที่ 2 — จัดการข้อมูล</text><text x="281" y="90" font-family="Segoe UI,sans-serif" font-size="11" fill="#94a3b8">ทำงานกับข้อมูลจำนวนมาก</text><rect x="281" y="102" width="198" height="40" rx="9" fill="#111827" stroke="#1f2937"/><circle cx="305" cy="122" r="13" fill="rgba(201,169,110,0.12)" stroke="#c9a96e" stroke-opacity="0.55"/><text x="305" y="127" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="11" font-weight="700" fill="#c9a96e">5</text><text x="327" y="127" font-family="Segoe UI,sans-serif" font-size="12.5" fill="#cbd5e1">ลิสต์ + วนลูป for</text><rect x="281" y="150" width="198" height="40" rx="9" fill="#111827" stroke="#1f2937"/><circle cx="305" cy="170" r="13" fill="rgba(201,169,110,0.12)" stroke="#c9a96e" stroke-opacity="0.55"/><text x="305" y="175" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="11" font-weight="700" fill="#c9a96e">6</text><text x="327" y="175" font-family="Segoe UI,sans-serif" font-size="12.5" fill="#cbd5e1">Dictionary</text><rect x="281" y="198" width="198" height="40" rx="9" fill="#111827" stroke="#1f2937"/><circle cx="305" cy="218" r="13" fill="rgba(201,169,110,0.12)" stroke="#c9a96e" stroke-opacity="0.55"/><text x="305" y="223" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="11" font-weight="700" fill="#c9a96e">7</text><text x="327" y="223" font-family="Segoe UI,sans-serif" font-size="12.5" fill="#cbd5e1">ฟังก์ชัน</text><rect x="281" y="246" width="198" height="40" rx="9" fill="#111827" stroke="#1f2937"/><circle cx="305" cy="266" r="13" fill="rgba(201,169,110,0.12)" stroke="#c9a96e" stroke-opacity="0.55"/><text x="305" y="271" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="11" font-weight="700" fill="#c9a96e">8</text><text x="327" y="271" font-family="Segoe UI,sans-serif" font-size="12.5" fill="#cbd5e1">อ่าน/เขียนไฟล์ CSV</text><polygon points="497,180 509,187 497,194" fill="#c9a96e" fill-opacity="0.7"/><rect x="510" y="45" width="230" height="272" rx="14" fill="#0f1626" stroke="#1f2937"/><text x="526" y="72" font-family="Segoe UI,sans-serif" font-size="13.5" font-weight="700" fill="#c9a96e">ช่วงที่ 3 — ของจริง</text><text x="526" y="90" font-family="Segoe UI,sans-serif" font-size="11" fill="#94a3b8">เอาไปใช้กับงานตัวเอง</text><rect x="526" y="102" width="198" height="40" rx="9" fill="#111827" stroke="#1f2937"/><circle cx="550" cy="122" r="13" fill="rgba(201,169,110,0.12)" stroke="#c9a96e" stroke-opacity="0.55"/><text x="550" y="127" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="11" font-weight="700" fill="#c9a96e">9</text><text x="572" y="127" font-family="Segoe UI,sans-serif" font-size="12.5" fill="#cbd5e1">อ่าน error ให้เป็น</text><rect x="526" y="150" width="198" height="40" rx="9" fill="#111827" stroke="#1f2937"/><circle cx="550" cy="170" r="13" fill="rgba(201,169,110,0.12)" stroke="#c9a96e" stroke-opacity="0.55"/><text x="550" y="175" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="11" font-weight="700" fill="#c9a96e">10</text><text x="572" y="175" font-family="Segoe UI,sans-serif" font-size="12.5" fill="#cbd5e1">ติดตั้ง Library (pip)</text><rect x="526" y="198" width="198" height="40" rx="9" fill="#111827" stroke="#1f2937"/><circle cx="550" cy="218" r="13" fill="rgba(201,169,110,0.12)" stroke="#c9a96e" stroke-opacity="0.55"/><text x="550" y="223" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="11" font-weight="700" fill="#c9a96e">11</text><text x="572" y="223" font-family="Segoe UI,sans-serif" font-size="12.5" fill="#cbd5e1">เรียก API</text><rect x="526" y="246" width="198" height="40" rx="9" fill="#111827" stroke="#1f2937"/><circle cx="550" cy="266" r="13" fill="rgba(201,169,110,0.12)" stroke="#c9a96e" stroke-opacity="0.55"/><text x="550" y="271" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="11" font-weight="700" fill="#c9a96e">12</text><text x="572" y="271" font-family="Segoe UI,sans-serif" font-size="12.5" fill="#cbd5e1">Capstone: สรุปยอด → LINE</text></svg>
:::

**ช่วงที่ 1 (EP1-4) พื้นฐาน** — เรียนรู้วิธีสั่งคอมพิวเตอร์ให้ทำตาม จบช่วงนี้คุณจะเขียนโปรแกรมคิดเงินลูกค้าพร้อมส่วนลดอัตโนมัติได้

**ช่วงที่ 2 (EP5-8) จัดการข้อมูล** — จากที่ทำงานกับข้อมูลทีละชิ้น เปลี่ยนเป็นทำกับข้อมูลทีละร้อยชิ้น จบช่วงนี้คุณจะเปิดไฟล์ยอดขายจาก Excel มาประมวลผลได้เอง

**ช่วงที่ 3 (EP9-12) ของจริง** — ช่วงที่คอร์สฟรีทั่วไปไม่ค่อยสอน ทั้งการแก้บั๊กด้วยตัวเอง การหยิบเครื่องมือที่คนอื่นเขียนไว้แล้วมาใช้ และการดึงข้อมูลจากอินเทอร์เน็ต

## ต้องเตรียมอะไรบ้าง

ข่าวดีคือแทบไม่ต้องเตรียมอะไรเลยครับ ไม่ต้องซื้ออะไรสักบาท

:::checklist
- คอมพิวเตอร์ 1 เครื่อง — Windows, Mac หรือ Linux ก็ได้ เครื่องเก่าก็ได้ ไม่ต้องแรง
- อินเทอร์เน็ต — ใช้ตอนติดตั้งโปรแกรมใน EP1 เท่านั้น หลังจากนั้นเรียนออฟไลน์ได้
- เวลาว่างประมาณ 45 นาทีต่อบทเรียน (อ่าน 15 นาที + ลงมือทำ 30 นาที)
- สมุดหรือไฟล์โน้ต 1 อัน — จดคำสั่งที่ใช้บ่อย จะช่วยได้มากในช่วงแรก
:::

:::note[💡] ไม่ต้องมีพื้นฐานอะไรเลย
ไม่ต้องเก่งเลข ไม่ต้องเก่งอังกฤษ ไม่ต้องเคยเรียนคอมพิวเตอร์มาก่อน ขอแค่ใช้คอมพิวเตอร์พื้นฐานเป็น — เปิดโฟลเดอร์ ติดตั้งโปรแกรม พิมพ์ไทย-อังกฤษได้ ก็พอแล้วครับ
:::

## วิธีเรียนให้จบจริง

สถิติของคอร์สออนไลน์ทั่วโลกคือมีคนเรียนจบไม่ถึง 15% ผมอยากให้คุณอยู่ในกลุ่มที่จบครับ จากประสบการณ์ มี 3 อย่างที่ทำให้คนเรียนจบต่างจากคนที่เลิกกลางทาง

:::step 1 พิมพ์โค้ดเอง อย่าก๊อปวาง
ฟังดูเสียเวลา แต่การพิมพ์เองทำให้คุณเจอ error และการเจอ error คือการเรียนรู้ที่แท้จริง คนที่ก๊อปวางตลอดจะรู้สึกว่าเข้าใจ แต่พอเขียนเองจริงจะเขียนไม่ออก
:::

:::step 2 ทำโจทย์ท้ายบททุกบท อย่างน้อยข้อแรก
ทุก EP มีโจทย์ 3 ข้อ ง่าย-กลาง-ท้าทาย ถ้าไม่มีเวลาจริงๆ ขอแค่ข้อแรกข้อเดียวก็ยังดี การอ่านอย่างเดียวโดยไม่ลงมือ เท่ากับดูคนอื่นออกกำลังกายแล้วหวังว่าตัวเองจะแข็งแรง
:::

:::step 3 อย่ารีบ และอย่าข้าม
แต่ละ EP ต่อยอดจาก EP ก่อนหน้าโดยตรง ถ้าอ่าน EP5 แล้วงง ให้กลับไปอ่าน EP4 ใหม่ ไม่ใช่ความผิดคุณ แปลว่าฐานยังไม่แน่นพอเท่านั้นเอง สัปดาห์ละ 1 EP คือจังหวะที่กำลังดี
:::

:::danger[🚫] กับดักที่เจอบ่อยที่สุด
"ขอดูให้จบทั้งคอร์สก่อน แล้วค่อยกลับมาลงมือทำทีเดียว" — วิธีนี้ไม่เคยได้ผลครับ เพราะพอถึงเวลาลงมือจริง คุณจะลืมของ EP1 ไปหมดแล้ว อ่านจบ 1 บท ลงมือทำ 1 บท เสมอ
:::

## พร้อมแล้วเริ่มกันเลย

EP1 เราจะติดตั้ง Python ลงเครื่องคุณ และเขียนโค้ดบรรทัดแรกให้รันได้จริงภายใน 20 นาที ไม่มีทฤษฎียาวๆ ไม่มีศัพท์เทคนิคที่ยังไม่จำเป็น — เปิดเครื่อง แล้วทำตามไปพร้อมกันเลยครับ

:::tip[🐶] จากหนูดี
ผมจะอยู่เป็นเพื่อนคุณตลอด 12 บทเรียนนี้ครับ ถ้าติดตรงไหน อ่านซ้ำแล้วยังไม่เข้าใจ ทักมาที่ LINE ได้เลย ไม่มีคำถามไหนโง่เกินไปสำหรับคนที่เพิ่งเริ่มครับ
:::
