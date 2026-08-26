<!-- ต้นฉบับ Markdown ของ Article #45 — แก้ที่นี่หรือใน Django admin ก็ได้ -->
<!-- title: EP2: ตัวแปรและชนิดข้อมูล — สร้างเครื่องคิดเลขคิดกำไรร้าน -->

โปรแกรมใน EP1 ของเราพูดได้อย่างเดียว บอกให้พูดอะไรก็พูด แต่จำอะไรไม่ได้เลย EP นี้เราจะให้มันมี "ความจำ" ครับ และพอมันจำได้ มันก็เริ่มคำนวณแทนเราได้ทันที

:::tip[🎯] จบ EP นี้คุณจะทำอะไรได้
สร้างตัวแปรเก็บค่าไว้ใช้ต่อได้ · แยกออกว่าข้อมูลแต่ละอย่างเป็นชนิดไหน · **เขียนเครื่องคิดเลขคิดกำไรร้านตัวเองได้ 1 ตัว**  
**ใช้เวลา:** อ่าน 15 นาที + ลงมือทำ 25 นาที · **ต้องผ่านมาก่อน:** EP1
:::

**ทบทวน 30 วินาที** — EP1 เราติดตั้ง Python กับ VS Code แล้วเขียน `print()` เพื่อแสดงข้อความบนจอ และรู้ว่าข้อความต้องมีเครื่องหมายคำพูดครอบ แต่ตัวเลขไม่ต้อง

## ตัวแปรคือกล่องที่ติดป้ายชื่อไว้

:::analogy 📦
ลองนึกถึง**กล่องเก็บของที่คุณเขียนป้ายแปะไว้ข้างกล่อง** เวลาจะใช้ของ คุณไม่ต้องจำว่าของอยู่ตรงไหน แค่เรียกชื่อบนป้ายก็หยิบถูก — ตัวแปรก็แบบเดียวกันเป๊ะ คุณเก็บค่าไว้ในกล่อง ตั้งชื่อกล่อง แล้วเรียกใช้ด้วยชื่อนั้นได้ตลอดทั้งโปรแกรม
:::

:::figure เครื่องหมาย = ไม่ได้แปลว่า "เท่ากับ" แต่แปลว่า "เอาค่าฝั่งขวา ใส่ลงกล่องฝั่งซ้าย"
<svg viewBox="0 0 760 240" role="img" aria-label="ไดอะแกรมเปรียบตัวแปรเป็นกล่องติดป้ายชื่อ เก็บค่าไว้ข้างใน" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="28" font-family="Segoe UI,sans-serif" font-size="13.5" font-weight="700" fill="#f1f5f9">ตัวแปร = กล่องที่ติดป้ายชื่อไว้</text>
  <rect x="20" y="48" width="220" height="110" rx="12" fill="#0f1626" stroke="#c9a96e" stroke-opacity="0.45"/>
  <rect x="44" y="38" width="90" height="22" rx="6" fill="#111827" stroke="#c9a96e" stroke-opacity="0.6"/>
  <text x="89" y="53" text-anchor="middle" font-family="Consolas,monospace" font-size="11.5" fill="#c9a96e">price</text>
  <text x="130" y="112" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="26" font-weight="700" fill="#e2e8f0">250</text>
  <text x="130" y="138" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="11" fill="#64748b">ตัวเลขจำนวนเต็ม (int)</text>
  <rect x="270" y="48" width="220" height="110" rx="12" fill="#0f1626" stroke="#c9a96e" stroke-opacity="0.45"/>
  <rect x="294" y="38" width="90" height="22" rx="6" fill="#111827" stroke="#c9a96e" stroke-opacity="0.6"/>
  <text x="339" y="53" text-anchor="middle" font-family="Consolas,monospace" font-size="11.5" fill="#c9a96e">cost</text>
  <text x="380" y="112" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="26" font-weight="700" fill="#e2e8f0">180</text>
  <text x="380" y="138" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="11" fill="#64748b">ตัวเลขจำนวนเต็ม (int)</text>
  <rect x="520" y="48" width="220" height="110" rx="12" fill="#0f1626" stroke="#c9a96e" stroke-opacity="0.45"/>
  <rect x="544" y="38" width="110" height="22" rx="6" fill="#111827" stroke="#c9a96e" stroke-opacity="0.6"/>
  <text x="599" y="53" text-anchor="middle" font-family="Consolas,monospace" font-size="11.5" fill="#c9a96e">shop_name</text>
  <text x="630" y="110" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="17" font-weight="700" fill="#e2e8f0">"ร้านหนูดี"</text>
  <text x="630" y="138" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="11" fill="#64748b">ข้อความ (str) — มีเครื่องหมายคำพูด</text>
  <rect x="20" y="182" width="720" height="44" rx="10" fill="#111827" stroke="#1f2937"/>
  <text x="40" y="209" font-family="Consolas,monospace" font-size="12.5" fill="#cbd5e1">price = 250</text>
  <text x="180" y="209" font-family="Segoe UI,sans-serif" font-size="12" fill="#94a3b8">อ่านว่า "เอาค่า 250 ใส่ลงในกล่องชื่อ price" — ลูกศรพุ่งจากขวาไปซ้ายเสมอ</text>
</svg>
:::

ลองสร้างไฟล์ใหม่ชื่อ `ep2.py` แล้วพิมพ์ตามนี้ครับ

```
shop_name = "ร้านกาแฟหนูดี"
price = 250

print(shop_name)
print(price)
```

ผลที่ได้

```
ร้านกาแฟหนูดี
250
```

สังเกตให้ดีนะครับ ตอนเราสั่ง `print(shop_name)` เราไม่ได้ใส่เครื่องหมายคำพูด เพราะเราไม่ได้อยากให้มันพิมพ์คำว่า "shop_name" ออกมา แต่อยากให้มัน**เปิดกล่องชื่อ shop_name แล้วเอาของข้างในออกมาพิมพ์**

```
print(shop_name)     # ได้: ร้านกาแฟหนูดี   ← เปิดกล่องเอาของข้างใน
print("shop_name")   # ได้: shop_name       ← พิมพ์ตัวหนังสือตรงๆ
```

:::note[💡] เครื่องหมาย # คืออะไร
ทุกอย่างที่อยู่หลัง `#` ในบรรทัดนั้น Python จะไม่สนใจเลย เราเรียกว่า **คอมเมนต์** มีไว้เขียนโน้ตบอกตัวเองในอนาคตว่าโค้ดตรงนี้ทำอะไร ใช้ให้ติดเป็นนิสัยตั้งแต่วันนี้เลยครับ คุณจะขอบคุณตัวเองในอีก 3 เดือน
:::

## ชนิดข้อมูล 4 แบบที่ต้องรู้

Python แยกข้อมูลออกเป็นชนิด และมันสำคัญมากเพราะ**ข้อมูลคนละชนิดทำอะไรกันไม่ได้** เหมือนคุณเอาน้ำหนัก 5 กิโลกรัม มาบวกกับ 3 ชั่วโมง แล้วถามว่าได้เท่าไหร่ — มันตอบไม่ได้

:::figure มีชนิดอื่นอีกเยอะ แต่ 4 ตัวนี้ครอบคลุมงานส่วนใหญ่ที่คุณจะเจอ
<svg viewBox="0 0 760 200" role="img" aria-label="ชนิดข้อมูล 4 แบบใน Python คือ str int float และ bool" xmlns="http://www.w3.org/2000/svg">
  <text x="20" y="26" font-family="Segoe UI,sans-serif" font-size="13.5" font-weight="700" fill="#f1f5f9">ชนิดข้อมูล 4 แบบที่ใช้จริง 95% ของงาน</text>
  <rect x="20" y="44" width="172" height="132" rx="12" fill="#0f1626" stroke="#1f2937"/>
  <text x="106" y="74" text-anchor="middle" font-family="Consolas,monospace" font-size="15" font-weight="700" fill="#c9a96e">str</text>
  <text x="106" y="96" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="12" fill="#cbd5e1">ข้อความ</text>
  <rect x="38" y="110" width="136" height="30" rx="7" fill="#111827"/>
  <text x="106" y="130" text-anchor="middle" font-family="Consolas,monospace" font-size="11.5" fill="#e2e8f0">"ร้านหนูดี"</text>
  <text x="106" y="160" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="10.5" fill="#64748b">ต้องมี " " ครอบเสมอ</text>
  <rect x="212" y="44" width="172" height="132" rx="12" fill="#0f1626" stroke="#1f2937"/>
  <text x="298" y="74" text-anchor="middle" font-family="Consolas,monospace" font-size="15" font-weight="700" fill="#c9a96e">int</text>
  <text x="298" y="96" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="12" fill="#cbd5e1">จำนวนเต็ม</text>
  <rect x="230" y="110" width="136" height="30" rx="7" fill="#111827"/>
  <text x="298" y="130" text-anchor="middle" font-family="Consolas,monospace" font-size="11.5" fill="#e2e8f0">250</text>
  <text x="298" y="160" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="10.5" fill="#64748b">ไม่มีจุดทศนิยม</text>
  <rect x="404" y="44" width="172" height="132" rx="12" fill="#0f1626" stroke="#1f2937"/>
  <text x="490" y="74" text-anchor="middle" font-family="Consolas,monospace" font-size="15" font-weight="700" fill="#c9a96e">float</text>
  <text x="490" y="96" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="12" fill="#cbd5e1">ทศนิยม</text>
  <rect x="422" y="110" width="136" height="30" rx="7" fill="#111827"/>
  <text x="490" y="130" text-anchor="middle" font-family="Consolas,monospace" font-size="11.5" fill="#e2e8f0">249.50</text>
  <text x="490" y="160" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="10.5" fill="#64748b">ใช้กับเงิน น้ำหนัก</text>
  <rect x="596" y="44" width="144" height="132" rx="12" fill="#0f1626" stroke="#1f2937"/>
  <text x="668" y="74" text-anchor="middle" font-family="Consolas,monospace" font-size="15" font-weight="700" fill="#c9a96e">bool</text>
  <text x="668" y="96" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="12" fill="#cbd5e1">จริง / เท็จ</text>
  <rect x="612" y="110" width="112" height="30" rx="7" fill="#111827"/>
  <text x="668" y="130" text-anchor="middle" font-family="Consolas,monospace" font-size="11.5" fill="#4ade80">True</text>
  <text x="668" y="160" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="10.5" fill="#64748b">ใช้ตอนตัดสินใจ</text>
</svg>
:::

ถ้าไม่แน่ใจว่าอะไรเป็นชนิดไหน ถาม Python ตรงๆ ได้ด้วยคำสั่ง `type()`

```
print(type("ร้านกาแฟหนูดี"))   # <class 'str'>
print(type(250))                # <class 'int'>
print(type(249.50))             # <class 'float'>
print(type(True))               # <class 'bool'>
```

คำว่า `class` ยังไม่ต้องสนใจครับ ดูแค่คำหลัง `'` ก็พอ

## คำนวณด้วยตัวแปร

พอค่าอยู่ในกล่องแล้ว เราเอากล่องมาบวกลบคูณหารกันได้เลย ตัวดำเนินการพื้นฐานมี 5 ตัว

```
a = 10
b = 3

print(a + b)    # 13    บวก
print(a - b)    # 7     ลบ
print(a * b)    # 30    คูณ  (ใช้ดอกจัน ไม่ใช่ x)
print(a / b)    # 3.333 หาร  (ได้ทศนิยมเสมอ)
print(a % b)    # 1     เศษจากการหาร
```

ที่ต้องระวังคือ **เครื่องหมายคูณคือ `*` ไม่ใช่ `x`** เพราะ x ถูกใช้เป็นชื่อตัวแปรได้ ถ้าเขียน `a x b` Python จะงงทันที

## สร้างเครื่องคิดเลขคิดกำไรร้าน

ถึงเวลาเอาของจริงมาใช้แล้วครับ สมมติว่าคุณขายกาแฟแก้วละ 250 บาท ต้นทุนแก้วละ 180 บาท วันนี้ขายได้ 12 แก้ว — เราจะให้คอมพิวเตอร์คำนวณให้

```
# ==== ข้อมูลของร้าน (แก้ตัวเลขตรงนี้ให้เป็นของร้านคุณ) ====
shop_name = "ร้านกาแฟหนูดี"
price = 250        # ราคาขายต่อแก้ว
cost = 180         # ต้นทุนต่อแก้ว
qty = 12           # จำนวนที่ขายได้วันนี้

# ==== คำนวณ ====
revenue = price * qty            # ยอดขาย
total_cost = cost * qty          # ต้นทุนรวม
profit = revenue - total_cost    # กำไร

# ==== แสดงผล ====
print("สรุปยอดวันนี้ของ", shop_name)
print("ขายได้", qty, "แก้ว")
print("ยอดขาย", revenue, "บาท")
print("ต้นทุน", total_cost, "บาท")
print("กำไร", profit, "บาท")
```

รันแล้วจะได้

```
สรุปยอดวันนี้ของ ร้านกาแฟหนูดี
ขายได้ 12 แก้ว
ยอดขาย 3000 บาท
ต้นทุน 2160 บาท
กำไร 840 บาท
```

ลองเปลี่ยนเลข `qty` จาก 12 เป็น 50 แล้วรันใหม่ครับ — ตัวเลขทุกบรรทัดเปลี่ยนตามให้เองหมด **นี่คือพลังของตัวแปร** คุณแก้ที่เดียว ที่เหลือมันคิดต่อให้เอง ถ้าเราไม่ใช้ตัวแปร คุณต้องนั่งแก้ตัวเลขทุกบรรทัดเอง

:::tip[💰] ลองต่อยอดเลย
เพิ่มบรรทัด `margin = profit / revenue * 100` แล้ว print ออกมา คุณจะได้ % กำไรของร้านทันที ซึ่งเป็นตัวเลขที่เจ้าของร้านควรรู้แต่ส่วนใหญ่ไม่เคยคำนวณ
:::

## กับดักที่คุณจะเจอ

:::danger[🚫] 1. เอาข้อความไปบวกกับตัวเลข
`"250" + 50` จะพังทันทีด้วย `TypeError` เพราะ `"250"` ที่มีคำพูดครอบคือ**ข้อความ** ไม่ใช่ตัวเลข ถ้าอยากแปลงให้ใช้ `int("250") + 50` จะได้ 300 — เรื่องนี้จะกลับมาหลอกหลอนคุณอีกครั้งใน EP3 ครับ จำไว้ให้ดี
:::

:::warn[⚠️] 2. ตั้งชื่อตัวแปรผิดกติกา
ห้ามขึ้นต้นด้วยตัวเลข (`2price` ไม่ได้) ห้ามมีเว้นวรรค (`shop name` ไม่ได้ ใช้ `shop_name`) และห้ามใช้คำสงวนของ Python เช่น `print`, `if`, `list` เป็นชื่อตัวแปร
:::

:::warn[⚠️] 3. ใช้ตัวแปรก่อนสร้าง
Python อ่านจากบนลงล่าง ถ้าคุณ `print(profit)` ก่อนบรรทัดที่คำนวณ `profit` จะเจอ `NameError: name 'profit' is not defined` แปลว่า "ไม่รู้จักกล่องชื่อนี้" — ต้องสร้างกล่องก่อนเสมอ แล้วค่อยเรียกใช้
:::

:::note[💡] ทำไมไม่ตั้งชื่อตัวแปรเป็นภาษาไทย
ทางเทคนิคทำได้ครับ `ราคา = 250` Python ยอมรับ แต่ผมไม่แนะนำ เพราะเวลาไปดูโค้ดคนอื่น ค้นหาวิธีแก้ปัญหาใน Google หรือให้ AI ช่วยเขียน ทุกอย่างเป็นภาษาอังกฤษหมด การชินกับชื่ออังกฤษตั้งแต่วันแรกจะช่วยคุณมากในระยะยาว ส่วน**คอมเมนต์เขียนไทยได้เต็มที่**ครับ
:::

## ลงมือทำ

**ข้อ 1 (ง่าย)** — สร้างตัวแปร 3 ตัวเก็บชื่อคุณ อายุ และส่วนสูง แล้ว print ออกมาทั้งหมด พร้อมเช็คด้วย `type()` ว่าแต่ละตัวเป็นชนิดอะไร

:::answer ดูเฉลยข้อ 1
```
name = "ภูมิพัฒน์"
age = 35
height = 172.5

print(name, age, height)
print(type(name))     # str
print(type(age))      # int
print(type(height))   # float
```
:::

**ข้อ 2 (กลาง)** — แก้เครื่องคิดเลขข้างบนให้คำนวณ**เปอร์เซ็นต์กำไร**เพิ่ม และให้แสดงผลว่า "กำไร 840 บาท (28.0%)"

:::answer ดูเฉลยข้อ 2
```
price = 250
cost = 180
qty = 12

revenue = price * qty
profit = (price - cost) * qty
margin = profit / revenue * 100

print("กำไร", profit, "บาท", "(", margin, "%)")
```

จะเห็นว่าผลออกมาหน้าตายังไม่สวย มีเว้นวรรคเกินรอบวงเล็บ และทศนิยมยาวเกินจำเป็น — EP3 เราจะได้เครื่องมือจัดข้อความให้สวยกว่านี้ครับ
:::

**ข้อ 3 (ท้าทาย)** — ร้านคุณมีสินค้า 2 อย่าง กาแฟ (ขาย 250 ทุน 180 ขายได้ 12) และเค้ก (ขาย 120 ทุน 70 ขายได้ 25) เขียนโปรแกรมสรุปกำไรรวมของทั้งร้าน และบอกด้วยว่าสินค้าไหนทำกำไรได้มากกว่า

:::answer ดูเฉลยข้อ 3
```
coffee_profit = (250 - 180) * 12    # 840
cake_profit = (120 - 70) * 25       # 1250
total = coffee_profit + cake_profit

print("กำไรกาแฟ", coffee_profit, "บาท")
print("กำไรเค้ก", cake_profit, "บาท")
print("กำไรรวม", total, "บาท")
```

เค้กทำกำไรมากกว่า (1,250 บาท) ทั้งที่ราคาถูกกว่าครึ่ง — ส่วนการให้โปรแกรม**ตอบเองว่าตัวไหนมากกว่า** ต้องใช้เงื่อนไข ซึ่งเป็นเรื่องของ EP4 ครับ
:::

## เช็คว่าคุณผ่าน EP นี้จริง

:::checklist
- อธิบายได้ว่า `price = 250` ทำงานยังไง และทำไม = ไม่ได้แปลว่า "เท่ากับ"
- บอกความต่างระหว่าง `250` กับ `"250"` ได้
- เครื่องคิดเลขกำไรของคุณรันได้ และเปลี่ยนตัวเลขแล้วผลลัพธ์เปลี่ยนตามถูกต้อง
- เขียนคอมเมนต์ด้วย `#` อธิบายโค้ดตัวเองได้
:::

## EP หน้าเจออะไร

ตอนนี้โปรแกรมของเรายังต้องให้คุณเข้าไปแก้ตัวเลขในโค้ดเองทุกครั้ง ซึ่งคนอื่นใช้ไม่ได้เลย EP3 เราจะทำให้โปรแกรม**ถามผู้ใช้เอง**ว่าขายอะไร กี่ชิ้น แล้วออกใบเสร็จหน้าตาสวยๆ ให้ พร้อมเรียนวิธีจัดข้อความให้ตัวเลขมีลูกน้ำคั่นหลักพันและทศนิยม 2 ตำแหน่งเป๊ะครับ
