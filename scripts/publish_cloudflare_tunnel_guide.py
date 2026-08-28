# -*- coding: utf-8 -*-
"""
Publish: วิธี Config Domain ใหม่บน Cloudflare Tunnel + Django Server
- Generate cover image via FLUX
- Generate diagrams via Pillow
- Publish draft to Django via management shell on server
"""
import os, sys, io, json, requests, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── Config ──────────────────────────────────────────────────────────────────
API_URL  = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
BASE_DIR = Path(__file__).resolve().parent.parent
FONT     = BASE_DIR / "Kanit-Bold.ttf"

from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")
HF_KEY   = os.getenv("HUGGINGFACE_API_KEY", "")
OUT_DIR  = BASE_DIR / "scripts" / "article_assets"
OUT_DIR.mkdir(exist_ok=True)

# ── Article Content ─────────────────────────────────────────────────────────
ARTICLE_TITLE = "วิธี Config Domain ใหม่บน Cloudflare Tunnel + Django Server (ฉบับทำจริง)"
ARTICLE_SLUG  = "config-domain-cloudflare-tunnel-django-server"
ARTICLE_BODY  = """
<h2>ระบบทำงานแบบนี้</h2>
<p>ก่อนเริ่ม ขอให้เข้าใจภาพรวมก่อน:</p>
<pre><code>Browser (ทั่วโลก)
     ↓
Cloudflare Network
     ↓
Cloudflare Tunnel (cloudflared daemon)
     ↓
Ubuntu Server 192.168.1.2 (LAN)
     ↓
Gunicorn port 8000 → Django App</code></pre>
<p><strong>ข้อดีของระบบนี้:</strong> ไม่ต้องมี Public IP จาก ISP, ไม่ต้องเปิด port บน router, Cloudflare รับ HTTPS แล้วส่งต่อผ่าน tunnel เข้า LAN</p>
[DIAGRAM_ARCHITECTURE]

<h2>ขั้นตอนที่ 1 — ตรวจสอบปัญหาก่อนแก้ (สำคัญมาก)</h2>
<p>ก่อนจะไปแตะอะไร ให้ตรวจ 3 จุดก่อนเสมอ</p>
<h3>เช็ค cloudflared logs</h3>
<pre><code>sudo journalctl -u cloudflared -f</code></pre>
<h3>เช็ค DNS records ใน Cloudflare Dashboard</h3>
<p>เข้า dash.cloudflare.com → เลือก domain → DNS → Records ถ้า domain ใช้ Cloudflare Tunnel ถูกต้อง DNS record จะเป็น CNAME ชี้ไปที่ <code>&lt;tunnel-id&gt;.cfargotunnel.com</code></p>

<h2>ขั้นตอนที่ 2 — Update cloudflared ให้เป็น version ล่าสุด</h2>
<pre><code>sudo apt-get update && sudo apt-get install cloudflared -y
cloudflared --version
sudo systemctl restart cloudflared
sudo systemctl status cloudflared</code></pre>
<p>ต้องเห็น <code>Active: active (running)</code> ถึงจะเดินต่อได้</p>

<h2>ขั้นตอนที่ 3 — แก้ ALLOWED_HOSTS ใน .env</h2>
<p>Django จะตอบ request จาก host ที่อยู่ใน list นี้เท่านั้น ถ้า domain ใหม่ไม่อยู่ใน list → Django ตอบกลับ <code>400 Bad Request</code> ทันที</p>
<pre><code>ALLOWED_HOSTS=192.168.1.2,localhost,noodee-bootbiz.com,www.noodee-bootbiz.com</code></pre>
<p>ใช้ sed แก้แบบ non-interactive:</p>
<pre><code>sed -i 's|ALLOWED_HOSTS=...(เดิม)...|ALLOWED_HOSTS=...(ใหม่)...|' .env</code></pre>

<h2>ขั้นตอนที่ 4 — เพิ่ม CSRF_TRUSTED_ORIGINS ใน settings.py</h2>
<p>Django ตั้งแต่ version 4.0 ต้องระบุ trusted origins ด้วย ถ้าไม่ใส่ → form ทุกอันจะขึ้น <code>403 CSRF verification failed</code></p>
<pre><code>CSRF_TRUSTED_ORIGINS = [
    'https://noodee-bootbiz.com',
    'https://www.noodee-bootbiz.com',
]</code></pre>
<p><strong>หมายเหตุ:</strong> ต้องใส่ <code>https://</code> นำหน้าเสมอ</p>

<h2>ขั้นตอนที่ 5 — Restart Django service</h2>
<pre><code>sudo systemctl restart peyo-agent
sudo systemctl status peyo-agent</code></pre>

<h2>ขั้นตอนที่ 6 — เพิ่ม Route ใน Cloudflare Zero Trust Dashboard</h2>
<p>ไปที่ <strong>one.dash.cloudflare.com</strong> → Networks → Tunnels → คลิก tunnel</p>
<p>⚠️ <strong>สำคัญมาก:</strong> ต้องใช้ tab <strong>"Published application routes"</strong> เท่านั้น ไม่ใช่ "Hostname routes (Beta)"</p>
<table>
<thead><tr><th>Tab</th><th>ใช้งานได้จริง</th></tr></thead>
<tbody>
<tr><td>Hostname routes (Beta)</td><td>❌ ไม่แนะนำ — ยังไม่ stable</td></tr>
<tr><td><strong>Published application routes</strong></td><td>✅ ใช้อันนี้</td></tr>
</tbody>
</table>
<p>คลิก <strong>"Add a published application route"</strong> แล้วกรอก:</p>
<ul>
<li>Subdomain: (เว้นว่าง)</li>
<li>Domain: noodee-bootbiz.com</li>
<li>Path: (เว้นว่าง — รับทุก path)</li>
<li>Type: HTTP</li>
<li>URL: localhost:8000</li>
</ul>
[DIAGRAM_DASHBOARD]

<h2>ขั้นตอนที่ 7 — ตรวจสอบว่าทุกอย่างทำงาน</h2>
<pre><code>sudo journalctl -u cloudflared -f</code></pre>
<p>ถ้า config update สำเร็จ จะเห็น: <code>Updated to new configuration</code> ที่มี domain ใหม่</p>

<h2>คำถามที่พบบ่อย (FAQ)</h2>
[DIAGRAM_FAQ]

<h3>Error 522 คืออะไร</h3>
<p><strong>522 Connection Timed Out</strong> หมายความว่า Cloudflare เชื่อมต่อมาถึง server แต่ server ไม่ตอบ สาเหตุที่พบบ่อย: Gunicorn ไม่รัน, cloudflared หยุดทำงาน, Route ชี้ไป port ผิด, ALLOWED_HOSTS ไม่มี domain</p>

<h3>หลาย domain ชี้มา port เดียวกันได้ไหม</h3>
<p>ได้ครับ ไม่มี conflict Cloudflare Tunnel รองรับ multiple hostnames ต่อ tunnel ได้ Django แยก domain ผ่าน <code>request.get_host()</code> ไม่ใช่ port</p>

<h3>ทำไม IP จริงของ server ไม่กระทบ</h3>
<p>เพราะ cloudflared ทำงานแบบ outbound connection ISP เปลี่ยน IP → ไม่กระทบเลย ย้าย server ไปอยู่ที่อื่น → แค่ run cloudflared ที่ใหม่ก็ใช้งานได้ทันที</p>

<h2>สรุป Checklist ครบ 10 ขั้น</h2>
[DIAGRAM_CHECKLIST]
"""

# ── Helper: hex → rgb ────────────────────────────────────────────────────────
def hex_to_rgb(h):
    h = h.lstrip("#")
    return int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)

def darken(rgb, f=0.55):
    return tuple(int(c*f) for c in rgb)

# ── Load Font ────────────────────────────────────────────────────────────────
def load_font(size):
    try:
        return ImageFont.truetype(str(FONT), size)
    except:
        return ImageFont.load_default()

# ── 1. Cover Image ───────────────────────────────────────────────────────────
def generate_cover():
    print("🎨 Generating cover image via FLUX...")
    prompt = (
        "cute chubby fat cartoon chocolate Labrador Retriever, "
        "sitting in front of glowing laptop computer screen, "
        "typing on keyboard focused expression, "
        "round pudgy belly cream colored tummy patch, "
        "big round black nose with light brown freckles, "
        "big round glossy eyes white highlight, "
        "floppy ears, rosy pink cheeks both sides, "
        "flat vector illustration kawaii style, "
        "dark navy blue gradient background, "
        "character positioned on right side of frame, "
        "no text, no watermark, full body"
    )
    r = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {HF_KEY}"},
        json={"inputs": prompt, "parameters": {"width": 1200, "height": 675, "num_inference_steps": 4}},
        timeout=90,
    )
    if r.status_code != 200 or not r.headers.get("content-type","").startswith("image"):
        print(f"  ❌ FLUX error {r.status_code}: {r.text[:200]}")
        return None

    img_bytes = r.content
    print("  ✅ FLUX image received, adding overlay...")

    # Overlay
    bg = "#0f1b35"  # Navy (educational)
    accent = "#c9a96e"  # Gold
    hook_lines = ["Config Domain", "ไม่ต้องมี IP จริง", "Tunnel ทำให้ได้เลย!"]

    img  = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    W, H = img.size
    draw = ImageDraw.Draw(img)

    bg_rgb     = hex_to_rgb(bg)
    accent_rgb = hex_to_rgb(accent)
    dark_rgb   = darken(accent_rgb)

    box_x2 = int(W * 0.54)
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.rectangle([0, 0, box_x2, H], fill=(*dark_rgb, 215))
    img  = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    # Diagonal stripe
    stripe_pts = [(box_x2-38,0),(box_x2+38,0),(box_x2+114,H),(box_x2,H)]
    draw.polygon(stripe_pts, fill=(*accent_rgb, 230))

    # Text sizes: line1=60, line2=80, line3=56
    sizes   = [60, 80, 56]
    colors  = [(*accent_rgb,255), (255,255,255,255), (212,175,55,255)]  # gold, white, deeper gold
    total_h = sum(s+14 for s in sizes)
    y       = (H - total_h)//2 - 10

    for i, (line, fs, color) in enumerate(zip(hook_lines, sizes, colors)):
        f = load_font(fs)
        draw.text((59, y+4), line, font=f, fill=(0,0,0,180))
        draw.text((55, y),   line, font=f, fill=color)
        y += fs + 14

    # Brand tag
    fb = load_font(22)
    tw, th = 170, 34
    tx, ty = W-tw-18, H-th-18
    draw.rounded_rectangle([tx,ty,tx+tw,ty+th], radius=7, fill=(*accent_rgb,200))
    draw.text((tx+10, ty+7), "AIBiz Thailand", font=fb, fill=(0,0,0,220))

    out = io.BytesIO()
    img.convert("RGB").save(out, format="JPEG", quality=93)
    cover_path = OUT_DIR / "cover_cloudflare_tunnel.jpg"
    cover_path.write_bytes(out.getvalue())
    print(f"  ✅ Cover saved: {cover_path}")
    return cover_path

# ── 2. Diagrams ──────────────────────────────────────────────────────────────
def make_diagram_architecture():
    W, H = 900, 380
    img  = Image.new("RGB", (W, H), "#0f1b35")
    draw = ImageDraw.Draw(img)
    f16  = load_font(16)
    f20  = load_font(20)
    f14  = load_font(14)

    gold = (201,169,110)
    white = (255,255,255)
    blue  = (96,165,250)

    steps = [
        ("🌐 Browser", "#1e3a5f"),
        ("☁️ Cloudflare", "#1e3a5f"),
        ("🔗 Tunnel (cloudflared)", "#1a3320"),
        ("🖥️ Ubuntu Server :LAN", "#1a3320"),
        ("⚡ Gunicorn :8000", "#2d1b69"),
        ("🐍 Django App", "#2d1b69"),
    ]
    box_w, box_h = 130, 52
    gap = 20
    total_w = len(steps)*(box_w+gap)-gap
    x_start = (W-total_w)//2
    y = (H-box_h)//2

    draw.text((W//2-180, 18), "สถาปัตยกรรมระบบ Cloudflare Tunnel", font=f20, fill=gold)

    for i,(label,bg) in enumerate(steps):
        x = x_start + i*(box_w+gap)
        bg_rgb = hex_to_rgb(bg)
        draw.rounded_rectangle([x,y,x+box_w,y+box_h], radius=8, fill=bg_rgb)
        draw.rounded_rectangle([x,y,x+box_w,y+box_h], radius=8, outline=gold, width=1)
        lines = label.split(" ")
        draw.text((x+8, y+8),  lines[0], font=f14, fill=white)
        draw.text((x+8, y+26), " ".join(lines[1:]) if len(lines)>1 else "", font=f14, fill=white)
        if i < len(steps)-1:
            ax = x+box_w+3; ay = y+box_h//2
            draw.line([(ax,ay),(ax+gap-4,ay)], fill=gold, width=2)
            draw.polygon([(ax+gap-4,ay-5),(ax+gap-4,ay+5),(ax+gap,ay)], fill=gold)

    note = "✅ ไม่ต้องมี Public IP  •  ✅ ไม่ต้องเปิด Port  •  ✅ IP เปลี่ยนก็ไม่กระทบ"
    draw.text((W//2-220, H-38), note, font=f14, fill=(100,200,100))

    path = OUT_DIR / "diag_architecture.png"
    img.save(path)
    print(f"  ✅ Diagram architecture: {path}")
    return path

def make_diagram_dashboard():
    W, H = 800, 300
    img  = Image.new("RGB", (W, H), "#0a0f1a")
    draw = ImageDraw.Draw(img)
    f18  = load_font(18)
    f15  = load_font(15)
    f13  = load_font(13)

    gold  = (201,169,110)
    white = (255,255,255)
    red   = (239,68,68)
    green = (74,222,128)

    draw.text((W//2-180, 16), "วิธีเพิ่ม Route ใน Zero Trust Dashboard", font=f18, fill=gold)

    rows = [
        ("Tab: Hostname routes (Beta)", "❌ ไม่แนะนำ", red, "#3f0e0e"),
        ("Tab: Published application routes", "✅ ใช้อันนี้!", green, "#064e3b"),
    ]
    y = 60
    for label, status, sc, bg in rows:
        bg_rgb = hex_to_rgb(bg)
        draw.rounded_rectangle([40,y,W-40,y+50], radius=8, fill=bg_rgb)
        draw.rounded_rectangle([40,y,W-40,y+50], radius=8, outline=sc, width=2)
        draw.text((60, y+14), label, font=f15, fill=white)
        draw.text((W-180, y+14), status, font=f15, fill=sc)
        y += 66

    draw.text((50, y+10), "กรอกข้อมูล:", font=f15, fill=gold)
    fields = ["Subdomain: (ว่างเปล่า)","Domain: noodee-bootbiz.com","Path: (ว่างเปล่า — รับทุก path)","Type: HTTP  |  URL: localhost:8000"]
    for i,f in enumerate(fields):
        draw.text((60, y+34+i*22), f"• {f}", font=f13, fill=white)

    path = OUT_DIR / "diag_dashboard.png"
    img.save(path)
    print(f"  ✅ Diagram dashboard: {path}")
    return path

def make_diagram_faq():
    W, H = 860, 280
    img  = Image.new("RGB", (W, H), "#0f1b35")
    draw = ImageDraw.Draw(img)
    f18  = load_font(18)
    f14  = load_font(14)
    f13  = load_font(13)

    gold  = (201,169,110)
    white = (255,255,255)
    red   = (252,165,165)
    green = (134,239,172)

    draw.text((W//2-130, 14), "Error 522 — สาเหตุและวิธีแก้", font=f18, fill=gold)

    headers = ["Error / ปัญหา", "สาเหตุ", "วิธีแก้"]
    col_w = [200, 300, 320]
    col_x = [20, 220, 520]
    y = 50
    for i,(h,x) in enumerate(zip(headers,col_x)):
        draw.rectangle([x,y,x+col_w[i]-4,y+28], fill=hex_to_rgb("#1e3a5f"))
        draw.text((x+8, y+6), h, font=f14, fill=gold)

    rows = [
        ("Error 522", "Gunicorn/cloudflared หยุด", "sudo systemctl restart"),
        ("404 Not Found", "Route ไม่ sync กับ tunnel", "ใช้ Published app routes"),
        ("403 CSRF Error", "ลืม CSRF_TRUSTED_ORIGINS", "เพิ่มใน settings.py"),
        ("400 Bad Request", "Domain ไม่ใน ALLOWED_HOSTS", "เพิ่มใน .env แล้ว restart"),
    ]
    y = 84
    for j,row in enumerate(rows):
        bg = hex_to_rgb("#0a1628" if j%2==0 else "#0d1f38")
        draw.rectangle([20,y,W-20,y+40], fill=bg)
        for i,(cell,x) in enumerate(zip(row,col_x)):
            color = red if i==0 else white if i==1 else green
            draw.text((x+8, y+12), cell, font=f13, fill=color)
        y += 42

    path = OUT_DIR / "diag_faq.png"
    img.save(path)
    print(f"  ✅ Diagram FAQ: {path}")
    return path

def make_diagram_checklist():
    W, H = 860, 340
    img  = Image.new("RGB", (W, H), "#0a0f1a")
    draw = ImageDraw.Draw(img)
    f20  = load_font(20)
    f15  = load_font(15)

    gold  = (201,169,110)
    white = (255,255,255)
    green = (74,222,128)

    draw.text((W//2-130, 14), "Checklist ครบ 10 ขั้นตอน", font=f20, fill=gold)

    steps = [
        "Update cloudflared → sudo apt-get install cloudflared -y",
        "เพิ่ม domain ใน ALLOWED_HOSTS (.env)",
        "เพิ่ม CSRF_TRUSTED_ORIGINS (settings.py)",
        "Restart Django → sudo systemctl restart peyo-agent",
        "ไป one.dash.cloudflare.com → Networks → Tunnels",
        "คลิก tunnel → tab \"Published application routes\"",
        "Add route: Domain, Type=HTTP, URL=localhost:8000",
        "Save → cloudflared รับ config ใหม่อัตโนมัติ",
        "ตรวจ logs: sudo journalctl -u cloudflared -f",
        "ทดสอบเปิด https://domain-ใหม่.com ✅",
    ]
    cols = 2
    per_col = 5
    col_w = W//2 - 30

    for i,step in enumerate(steps):
        col = i//per_col
        row = i%per_col
        x = 20 + col*(col_w+20)
        y = 55 + row*52
        bg = hex_to_rgb("#1a3320" if i<5 else "#1e3a5f")
        draw.rounded_rectangle([x,y,x+col_w,y+44], radius=6, fill=bg)
        draw.rounded_rectangle([x,y,x+col_w,y+44], radius=6, outline=gold, width=1)
        draw.text((x+10, y+6),  f"{i+1:02d}", font=f15, fill=gold)
        draw.text((x+44, y+13), step, font=load_font(13), fill=white)

    path = OUT_DIR / "diag_checklist.png"
    img.save(path)
    print(f"  ✅ Diagram checklist: {path}")
    return path

# ── 3. Insert diagram tags into body ─────────────────────────────────────────
def build_body_with_diagrams(arch_path, dash_path, faq_path, check_path):
    """แทน [DIAGRAM_*] ด้วย img tag — path สัมพัทธ์จะถูกอัปโหลดพร้อม publish"""
    body = ARTICLE_BODY
    body = body.replace("[DIAGRAM_ARCHITECTURE]",
        f'<p><img src="PLACEHOLDER_ARCH" alt="สถาปัตยกรรมระบบ Cloudflare Tunnel" style="width:100%;border-radius:8px;margin:16px 0"></p>')
    body = body.replace("[DIAGRAM_DASHBOARD]",
        f'<p><img src="PLACEHOLDER_DASH" alt="วิธีเพิ่ม Route ใน Cloudflare Dashboard" style="width:100%;border-radius:8px;margin:16px 0"></p>')
    body = body.replace("[DIAGRAM_FAQ]",
        f'<p><img src="PLACEHOLDER_FAQ" alt="ตาราง Error 522" style="width:100%;border-radius:8px;margin:16px 0"></p>')
    body = body.replace("[DIAGRAM_CHECKLIST]",
        f'<p><img src="PLACEHOLDER_CHECK" alt="Checklist 10 ขั้นตอน" style="width:100%;border-radius:8px;margin:16px 0"></p>')
    return body

# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n=== Article Publisher: Cloudflare Tunnel Guide ===\n")

    # Step 1: Cover
    cover_path = generate_cover()

    # Step 2: Diagrams
    print("\n📊 Generating diagrams...")
    arch_path  = make_diagram_architecture()
    dash_path  = make_diagram_dashboard()
    faq_path   = make_diagram_faq()
    check_path = make_diagram_checklist()

    # Step 3: Build body
    body = build_body_with_diagrams(arch_path, dash_path, faq_path, check_path)

    # Step 4: Save publish payload
    payload = {
        "title":    ARTICLE_TITLE,
        "slug":     ARTICLE_SLUG,
        "body":     body,
        "cover":    str(cover_path) if cover_path else "",
        "diagrams": {
            "architecture": str(arch_path),
            "dashboard":    str(dash_path),
            "faq":          str(faq_path),
            "checklist":    str(check_path),
        },
        "category": "behind-the-scenes",
        "status":   "draft",
    }
    payload_path = OUT_DIR / "publish_payload.json"
    payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ Payload saved: {payload_path}")
    print(f"\n📋 Summary:")
    print(f"   Cover  : {'✅' if cover_path else '❌'}")
    print(f"   Diagrams: arch ✅  dashboard ✅  faq ✅  checklist ✅")
    print(f"\nReady to publish → run django-blog-publisher skill next")
