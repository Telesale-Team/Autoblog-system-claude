"""
Seed 3 OpenClaw articles for the blog.
Run: python manage.py shell < scripts/seed_openclaw_articles.py
"""

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from blog.models import Article, Category, Tag


User = get_user_model()
author = User.objects.filter(is_superuser=True).first()

if not author:
    print("ERROR: no superuser found")
    raise SystemExit

cat_edu = Category.objects.get(slug="educational")
cat_insight = Category.objects.get(slug="insights")


def get_or_create_tag(name):
    slug_map = {
        "OpenClaw": "openclaw", "AI Gateway": "ai-gateway",
        "Self-Hosted": "self-hosted", "LINE": "line",
        "PDPA": "pdpa", "SME": "sme", "Tutorial": "tutorial",
        "AI Chatbot": "ai-chatbot", "How-to": "how-to",
    }
    slug = slug_map.get(name, name.lower())
    tag, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": name})
    return tag


# =========================================================================
# Article 1 — Educational: OpenClaw คืออะไร
# =========================================================================
A1_TITLE = "OpenClaw คืออะไร? ทำไม SME ไทยควรรู้จัก AI Gateway แบบ Self-Hosted"
A1_EXCERPT = (
    "ทำความรู้จัก OpenClaw — AI Gateway แบบ open-source ที่ติดตั้งบน server "
    "ของคุณเอง เชื่อม LINE, Telegram, WhatsApp กับ Claude/GPT/Gemini "
    "พร้อมเหตุผลว่าทำไมมันเหมาะกับ SME ไทยมากกว่า SaaS Chatbot ทั่วไป"
)
A1_CONTENT = """<p>ในยุคที่ทุกธุรกิจพูดถึง AI กัน เจ้าของกิจการ SME หลายคนคงเริ่มมองหาวิธีนำ AI Chatbot มาใช้ตอบลูกค้า แต่พอลองหาข้อมูล กลับเจอตัวเลือกที่แพงกว่าที่คิด หรือไม่ก็ต้องส่งข้อมูลลูกค้าออกไปบน cloud ของบริษัทต่างประเทศ</p>

<p><strong>OpenClaw</strong> คือคำตอบสำหรับโจทย์นี้ — โปรเจกต์ open-source ที่กำลังมาแรงในวงการ AI Automation ที่ออกแบบมาให้ติดตั้งบน server ของคุณเองได้ และเชื่อมต่อกับ AI ได้ทุกค่ายในตลาด</p>

<h2>OpenClaw ทำงานอย่างไร</h2>
<p>OpenClaw ทำหน้าที่เป็น "Gateway" หรือสะพานเชื่อมระหว่าง 3 ส่วนหลัก:</p>
<ol>
  <li><strong>ช่องทางสื่อสาร (Channels)</strong> — LINE, Telegram, WhatsApp, Facebook Messenger, WebChat, Slack, Discord และอื่น ๆ รวม 28+ ช่องทาง</li>
  <li><strong>AI Models</strong> — Claude, GPT-4, Gemini, Llama, Mistral, Ollama (LLM ที่รัน local) รวม 35+ providers</li>
  <li><strong>ระบบฝั่งคุณ</strong> — ฐานข้อมูลลูกค้า, CRM, ERP, ระบบสต็อก ฯลฯ</li>
</ol>

<p>เมื่อมีข้อความเข้ามาจากช่องทางใดก็ตาม OpenClaw จะรับ ส่งให้ AI ประมวลผล แล้วตอบกลับลูกค้าโดยอัตโนมัติ ทั้งหมดเกิดขึ้นบน server ของคุณเอง</p>

<h2>ความต่างจาก Chatbot ทั่วไปในตลาด</h2>
<p>Chatbot SaaS อย่าง Chatfuel, ManyChat หรือ Dialogflow มีข้อดีคือใช้งานง่าย แต่มีข้อจำกัดสำคัญ:</p>
<ul>
  <li>ข้อมูลลูกค้าทั้งหมดวิ่งผ่าน server ของผู้ให้บริการ — เป็นความเสี่ยงด้าน <strong>PDPA</strong></li>
  <li>คิดเงินแบบ per-message หรือ per-user — ยิ่งใช้เยอะ ยิ่งจ่ายแพง</li>
  <li>ผูกกับ AI provider เดียว ย้ายไม่ได้</li>
  <li>ปรับแต่งได้จำกัด ทำ workflow ซับซ้อนยาก</li>
</ul>

<p>OpenClaw แก้ปัญหาเหล่านี้ทั้งหมด เพราะเป็น <strong>self-hosted</strong> และ <strong>MIT License</strong> — แปลว่าโค้ดทั้งหมดเป็นของคุณ ใช้เชิงพาณิชย์ได้ ไม่มีค่ารายเดือนผูกมัด</p>

<h2>ทำไม SME ไทยถึงเหมาะ</h2>
<p>SME ไทยส่วนใหญ่มีลูกค้าหลักอยู่บน LINE และต้องคำนึงถึง พ.ร.บ. คุ้มครองข้อมูลส่วนบุคคล (PDPA) ที่บังคับใช้แล้วตั้งแต่ปี 2565 OpenClaw ตอบโจทย์ทั้งสองข้อนี้พอดี:</p>

<blockquote>
"ข้อมูลลูกค้าไม่ออกนอกบริษัท" คือคำที่ลูกค้าทุกรายของเราพอใจมากที่สุด หลังเปลี่ยนจาก SaaS chatbot เดิม
</blockquote>

<p>นอกจากนี้ การจ่ายแบบครั้งเดียว + ค่า maintenance รายเดือน ทำให้ <strong>ประหยัดกว่า SaaS 60-80%</strong> เมื่อคำนวณค่าใช้จ่ายระยะยาว 3 ปี โดยเฉพาะธุรกิจที่มี volume ข้อความเยอะ</p>

<h2>ใครเหมาะ ใครยังไม่เหมาะ</h2>
<p><strong>เหมาะกับคุณถ้า:</strong></p>
<ul>
  <li>มีลูกค้าทักผ่าน LINE/Telegram มากกว่า 100 คน/วัน</li>
  <li>ทีม CS ทำไม่ทัน หรืออยากตอบ 24/7</li>
  <li>กังวลเรื่องข้อมูลลูกค้ารั่วหรือ PDPA</li>
  <li>อยากควบคุมระบบเองทั้งหมด ไม่ผูกขาดกับ vendor</li>
</ul>

<p><strong>ยังไม่เหมาะถ้า:</strong></p>
<ul>
  <li>มีลูกค้าทักน้อยมาก (&lt; 20 คน/วัน) — SaaS plan ฟรี/ถูกอาจคุ้มกว่า</li>
  <li>ไม่มีทีม IT เลย และไม่ต้องการจ้างคนดูแลระบบ</li>
</ul>

<h2>สรุป</h2>
<p>OpenClaw คือทางเลือกที่ลงตัวระหว่าง <em>"ใช้งานง่ายแบบ SaaS"</em> กับ <em>"ควบคุมข้อมูลเองแบบ on-premise"</em> สำหรับ SME ไทยที่กำลังมองหาระบบ AI Chatbot ที่จริงจัง ไม่ใช่ของเล่น และไม่ต้องการเสี่ยงเรื่อง PDPA หรือค่าใช้จ่ายที่บานปลาย</p>

<p>ในบทความถัดไป เราจะลงลึกเรื่อง <strong>"5 เหตุผลที่ AI Gateway ดีกว่า SaaS Chatbot"</strong> และ <strong>"วิธีตั้งค่า OpenClaw เชื่อม LINE ใน 5 นาที"</strong> ติดตามได้เลยครับ</p>
"""

# =========================================================================
# Article 2 — Insight: 5 เหตุผล
# =========================================================================
A2_TITLE = "5 เหตุผลที่ AI Gateway บน Server ตัวเอง ดีกว่า SaaS Chatbot สำหรับธุรกิจไทย"
A2_EXCERPT = (
    "เทียบให้เห็นชัด ๆ ว่าทำไม AI Gateway แบบ self-hosted ถึงเหมาะกับ "
    "SME ไทยมากกว่า SaaS chatbot ทั่วไป — ทั้งเรื่องราคา, PDPA, "
    "การควบคุม, scaling และความยืดหยุ่นในระยะยาว"
)
A2_CONTENT = """<p>ทุกครั้งที่เราพูดคุยกับเจ้าของ SME ไทยเรื่อง AI Chatbot คำถามแรกที่เจอเสมอคือ "แล้วต่างจาก ManyChat หรือ Chatfuel ยังไง?" บทความนี้จะตอบให้เห็นภาพชัดที่สุด ผ่าน 5 เหตุผลที่ทำให้ AI Gateway แบบ self-hosted (เช่น OpenClaw) เหนือกว่าในระยะยาว</p>

<h2>1. ค่าใช้จ่ายระยะยาวต่างกันเป็นเท่าตัว</h2>
<p>SaaS Chatbot คิดเงินแบบ subscription รายเดือน + บางเจ้าคิด per-message อีก ตัวอย่างชัดเจน:</p>
<ul>
  <li>ManyChat Pro: $15-30/เดือน + ขึ้นตาม subscriber → ปีละ 6,000-15,000 บาท</li>
  <li>Chatfuel Premium: $14.99-79.99/เดือน → ปีละ 6,000-32,000 บาท</li>
  <li>Botpress, Tidio, Intercom: $39-200/เดือน → ปีละ 15,000-80,000+ บาท</li>
</ul>
<p>เทียบกับ self-hosted: <strong>จ่ายค่า setup ครั้งเดียว 15,000-80,000 + maintenance 2,000-8,000/เดือน</strong> ที่ไม่ขึ้นตาม volume ข้อความ คำนวณ 3 ปี ประหยัดกว่า 50-70% โดยเฉพาะถ้ามีลูกค้าเยอะ</p>

<h2>2. ข้อมูลลูกค้าไม่ออกนอกบริษัท = PDPA-Safe จริง</h2>
<p>นี่คือเหตุผลที่ <strong>คลินิก, สำนักงานกฎหมาย, สถาบันการเงิน</strong> ในไทยเลือก self-hosted กันเกือบทั้งหมด เพราะ:</p>

<blockquote>
พ.ร.บ. คุ้มครองข้อมูลส่วนบุคคล (PDPA) กำหนดโทษปรับสูงสุด <strong>5 ล้านบาท</strong> สำหรับการประมวลผลข้อมูลส่วนบุคคลโดยไม่ได้รับความยินยอม หรือไม่มีมาตรการรักษาความปลอดภัยที่เหมาะสม
</blockquote>

<p>เมื่อข้อมูลลูกค้าวิ่งผ่าน server ของผู้ให้บริการ SaaS ที่ไหนก็ไม่รู้ในต่างประเทศ คุณต้อง:</p>
<ul>
  <li>มี Data Processing Agreement (DPA) ที่ชัดเจน</li>
  <li>ตรวจสอบว่า vendor มี certification (เช่น ISO 27001, SOC 2)</li>
  <li>แจ้งลูกค้าว่าข้อมูลถูกประมวลผลที่ไหน</li>
</ul>
<p>ในขณะที่ self-hosted = ข้อมูลทุกอย่างอยู่บน server ของคุณ ไม่ต้องเซ็น DPA ใด ๆ ความเสี่ยงเหลือศูนย์</p>

<h2>3. AI Multi-Provider — ไม่ผูกขาดกับใคร</h2>
<p>นี่คือข้อได้เปรียบที่หลายคนมองข้าม SaaS Chatbot ส่วนใหญ่ผูกกับ AI provider เดียว (มัก OpenAI) ถ้าวันนึง:</p>
<ul>
  <li>OpenAI ขึ้นราคา → คุณไม่มีทางเลือก</li>
  <li>OpenAI ล่ม → bot คุณก็ล่ม</li>
  <li>มี AI ใหม่ที่เก่งกว่า/ถูกกว่า → ย้ายไม่ได้</li>
</ul>
<p>OpenClaw และ AI Gateway แนวเดียวกันรองรับ <strong>35+ LLM providers</strong> สลับได้ในไม่กี่นาทีแค่เปลี่ยน config ไม่ต้องเขียนโค้ดใหม่</p>

<h2>4. Customization ที่ทำได้จริง ไม่ใช่แค่หน้าตา</h2>
<p>SaaS chatbot ส่วนใหญ่ให้ customize ได้แค่ flow และข้อความ แต่พอจะทำอะไรซับซ้อน เช่น:</p>
<ul>
  <li>เชื่อม CRM/ERP ของบริษัทเอง</li>
  <li>ดึงข้อมูลจากฐานข้อมูล real-time</li>
  <li>Multi-agent — แบ่ง AI หลายตัวทำหน้าที่ต่างกัน (sales/support/internal)</li>
  <li>Custom workflow ที่ต้องเรียก API หลายเส้น</li>
</ul>
<p>ก็จะเจอข้อจำกัด หรือต้องจ่าย Enterprise plan แพงมาก ในขณะที่ self-hosted = เขียน code เองได้ทั้งหมด ไม่มีลิมิต</p>

<h2>5. Scale ไม่กลัว — เพราะค่าใช้จ่ายไม่พุ่ง</h2>
<p>ปัญหาที่เจอบ่อยมากในธุรกิจที่โต: SaaS plan เริ่มจาก 1,000 subscribers ฟรี แต่พอ 10,000 → 50,000 → 100,000 ราคากระโดด exponential</p>
<p>self-hosted บน VPS เริ่มต้น 300-500 บาท/เดือน รองรับได้ <strong>หลักหมื่นถึงแสน users</strong> ก่อนต้อง upgrade server ค่าใช้จ่ายเพิ่มแบบ linear ไม่ใช่ exponential</p>

<h2>แล้วเมื่อไหร่ SaaS เหมาะกว่า?</h2>
<p>SaaS chatbot ก็มีจุดเด่น โดยเฉพาะถ้า:</p>
<ul>
  <li>คุณต้องการ launch ภายใน 1-2 วัน ไม่มีทีม IT</li>
  <li>Volume ข้อความน้อยมาก (&lt; 1,000 messages/เดือน)</li>
  <li>ไม่มี sensitive data ที่กังวล PDPA</li>
  <li>ต้องการ no-code visual flow builder</li>
</ul>

<h2>สรุป</h2>
<p>ถ้าธุรกิจคุณเริ่มจริงจัง — มีลูกค้าทักเข้ามาทุกวัน, มีข้อมูลที่อ่อนไหว, อยากควบคุมระยะยาว — <strong>AI Gateway แบบ self-hosted คือคำตอบที่ลงทุนคุ้มกว่ามาก</strong> โดยเฉพาะเมื่อมองในแง่ ROI 3 ปี</p>

<p>บทความถัดไปเราจะแสดงวิธีตั้งค่า OpenClaw เชื่อม LINE จริง ๆ ใน 5 นาที</p>
"""

# =========================================================================
# Article 3 — Educational/How-to: คู่มือเริ่มต้น
# =========================================================================
A3_TITLE = "คู่มือเริ่มต้น: ตั้งค่า OpenClaw เชื่อม LINE ใน 5 นาที (ฉบับ SME)"
A3_EXCERPT = (
    "Step-by-step สำหรับเจ้าของ SME ที่อยากลอง deploy OpenClaw เชื่อม LINE "
    "Official Account เข้ากับ AI ตั้งแต่ขั้นเตรียม VPS, ตั้ง webhook, "
    "config AI provider จนถึงการทดสอบครั้งแรก"
)
A3_CONTENT = """<p>หลังจากบทความแนะนำ OpenClaw และเหตุผลที่ควรเลือก self-hosted ครั้งนี้เรามาลงมือจริง — คู่มือทีละขั้นตอนสำหรับการตั้งค่า OpenClaw เชื่อม LINE Official Account ให้ AI ตอบลูกค้าอัตโนมัติ</p>

<blockquote>
หมายเหตุ: บทความนี้เน้นภาพรวมและแนวคิด ไม่ใช่ technical doc ของ OpenClaw — สำหรับขั้นตอนละเอียดยิบ ดูที่ docs.openclaw.ai
</blockquote>

<h2>สิ่งที่ต้องเตรียม</h2>
<ul>
  <li><strong>VPS</strong> Linux (Ubuntu 22.04+) อย่างน้อย 2 GB RAM, 20 GB SSD — แนะนำ Hostinger, DigitalOcean, Cloudways (ราคาเริ่มต้น 200-500 บาท/เดือน)</li>
  <li><strong>LINE Official Account</strong> + LINE Developers account (ฟรี ที่ <code>developers.line.biz</code>)</li>
  <li><strong>API Key</strong> ของ LLM ที่จะใช้ (Claude/OpenAI/Gemini) — ราคาเริ่มต้นประมาณ $5</li>
  <li><strong>Domain name</strong> 1 ตัว สำหรับ webhook (เช่น <code>bot.yourcompany.co.th</code>)</li>
</ul>

<h2>ขั้นที่ 1: ติดตั้ง OpenClaw บน VPS</h2>
<p>หลัง SSH เข้า VPS แล้ว วิธีที่ง่ายที่สุดคือใช้ Docker:</p>
<pre><code>curl -fsSL https://get.openclaw.ai/install.sh | bash</code></pre>
<p>script จะติดตั้ง Docker, Docker Compose, และ pull image OpenClaw มาให้พร้อมใช้ ใช้เวลาประมาณ 2-3 นาที</p>

<h3>ตั้งค่า config เริ่มต้น</h3>
<p>OpenClaw จะถาม:</p>
<ul>
  <li>ชื่อโปรเจกต์</li>
  <li>Admin email + password</li>
  <li>Port ที่จะรัน (default 8080)</li>
</ul>
<p>เสร็จแล้วเข้า dashboard ผ่านเบราว์เซอร์: <code>http://your-server-ip:8080</code></p>

<h2>ขั้นที่ 2: ตั้งค่า LINE Channel</h2>
<p>ที่ LINE Developers Console:</p>
<ol>
  <li>สร้าง <strong>Provider</strong> และ <strong>Messaging API channel</strong></li>
  <li>คัดลอก <code>Channel Secret</code> และ <code>Channel Access Token</code></li>
  <li>ปิด "Auto-reply messages" และ "Greeting messages" (ป้องกัน LINE ตอบทับ AI)</li>
</ol>

<h3>เพิ่ม channel ใน OpenClaw</h3>
<p>ที่ dashboard กด <em>Channels → Add new → LINE</em> วาง 2 ค่าที่คัดลอกมา OpenClaw จะคืนค่า <strong>Webhook URL</strong> ให้</p>

<h3>ตั้ง webhook ที่ LINE</h3>
<p>กลับไปที่ LINE Developers Console → Messaging API → Webhook URL → วาง URL ที่ได้ → กด <em>Verify</em></p>

<p>ถ้าขึ้น <strong>Success</strong> แปลว่าเชื่อมต่อสำเร็จแล้ว!</p>

<h2>ขั้นที่ 3: ตั้งค่า AI Agent</h2>
<p>ที่ <em>Agents → Create new</em>:</p>
<ul>
  <li><strong>Provider</strong>: เลือก Claude, OpenAI, หรือ Gemini</li>
  <li><strong>API Key</strong>: ใส่ API key ที่ได้</li>
  <li><strong>Model</strong>: แนะนำ <code>claude-haiku</code> หรือ <code>gpt-4o-mini</code> (ถูก + เร็ว) สำหรับ SME ทั่วไป</li>
  <li><strong>System Prompt</strong>: เขียนบทบาท เช่น "คุณคือพนักงาน CS ของร้าน X ตอบคำถามลูกค้าเรื่องสินค้า ราคา และการจัดส่ง อย่างเป็นมิตร ใช้ภาษาไทย"</li>
</ul>

<h2>ขั้นที่ 4: เชื่อม Agent กับ Channel</h2>
<p>ที่ <em>Routing → New rule</em>:</p>
<ul>
  <li>Channel: เลือก LINE channel ที่สร้างไว้</li>
  <li>Agent: เลือก agent ที่สร้างไว้</li>
  <li>Memory: เปิด <strong>Per-user session</strong> เพื่อให้ AI จำบทสนทนาของลูกค้าแต่ละคนได้</li>
</ul>

<h2>ขั้นที่ 5: ทดสอบ</h2>
<p>เพิ่ม LINE OA เป็นเพื่อน → ส่งข้อความทักทาย → AI ควรตอบกลับภายใน 2-3 วินาที</p>

<p>ถ้า AI ไม่ตอบ ลอง check:</p>
<ul>
  <li>Webhook URL valid และ HTTPS (LINE บังคับ)</li>
  <li>API key ของ AI ถูกต้องและมี credit เหลือ</li>
  <li>Log ใน OpenClaw dashboard (มีบอกชัดเจนว่าผิดที่ขั้นไหน)</li>
</ul>

<h2>Tips สำหรับ SME</h2>
<ol>
  <li><strong>เริ่มที่ Claude Haiku หรือ GPT-4o-mini</strong> — ค่าใช้จ่ายประมาณ 500-2,000 บาท/เดือน สำหรับ traffic SME ทั่วไป</li>
  <li><strong>System prompt ดี = บอทดี</strong> ใช้เวลาเขียน prompt ให้ละเอียด ระบุรายการสินค้า/ราคา/นโยบายไว้เลย</li>
  <li><strong>ตั้ง confidence threshold + human handoff</strong> — เมื่อ AI ไม่แน่ใจ ส่งต่อให้ทีมงานทันที (สำคัญมากในธุรกิจที่ผิดไม่ได้)</li>
  <li><strong>ดู log ทุกวัน 1-2 สัปดาห์แรก</strong> — จะเห็น pattern ว่าลูกค้าถามอะไร แล้วปรับ prompt ให้ดีขึ้นเรื่อย ๆ</li>
</ol>

<h2>สรุป</h2>
<p>การ deploy OpenClaw ครั้งแรกใช้เวลาจริง ๆ ประมาณ 30-60 นาที ถ้ามีพื้นฐาน Linux เบื้องต้น สำหรับ SME ที่ไม่มีทีม IT แนะนำให้ใช้บริการติดตั้งกับ vendor (เริ่ม 15,000 บาท) จะคุ้มกว่ามากเพราะได้ทั้ง training + maintenance plan</p>

<p>หลัง deploy แล้ว สิ่งที่จะได้ทันที: <strong>ลูกค้าได้คำตอบ 24/7</strong>, <strong>ทีม CS เหลือเวลาทำงานสำคัญ</strong>, และ <strong>ข้อมูลทุกอย่างอยู่บน server คุณเอง</strong></p>
"""


def upsert_article(title, slug, excerpt, content, category, tag_names, days_ago=0):
    article, created = Article.objects.update_or_create(
        slug=slug,
        defaults={
            "title": title,
            "author": author,
            "category": category,
            "excerpt": excerpt,
            "content": content,
            "status": "published",
            "is_featured": True,
            "published_at": timezone.now() - timedelta(days=days_ago),
        },
    )
    article.tags.set([get_or_create_tag(t) for t in tag_names])
    print(f"{'CREATED' if created else 'UPDATED'}: {title}")
    return article


upsert_article(
    A1_TITLE, "openclaw-introduction-for-thai-sme", A1_EXCERPT, A1_CONTENT, cat_edu,
    ["OpenClaw", "AI Gateway", "Self-Hosted", "SME"], days_ago=2,
)

upsert_article(
    A2_TITLE, "5-reasons-ai-gateway-better-than-saas", A2_EXCERPT, A2_CONTENT, cat_insight,
    ["AI Gateway", "PDPA", "SME", "AI Chatbot"], days_ago=1,
)

upsert_article(
    A3_TITLE, "openclaw-line-setup-in-5-minutes", A3_EXCERPT, A3_CONTENT, cat_edu,
    ["OpenClaw", "LINE", "Tutorial", "How-to"], days_ago=0,
)

# Clean up old Thai-slug versions if any
from blog.models import Article as _A
_A.objects.filter(slug__in=[
    "openclaw-คือ-อะไร",
    "5-เหตุผล-ai-gateway-vs-saas",
    "openclaw-line-ตั้งค่า-5-นาที",
]).delete()

print()
print(f"Total published articles: {Article.objects.filter(status='published').count()}")
