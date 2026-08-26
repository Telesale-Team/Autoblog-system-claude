# -*- coding: utf-8 -*-
"""
Generate หนูดี Mascot Logo Preview
- navbar_logo.png : ใช้แทน brand text ใน navbar (transparent bg)
- favicon_64.png  : preview favicon ขนาด 64x64
- favicon_32.png  : favicon จริง
"""
import os, io, sys, requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

HF_KEY  = "REMOVED_SEE_DOTENV"
API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

OUT_DIR = BASE_DIR / "scripts" / "logo_preview"
OUT_DIR.mkdir(exist_ok=True)

FONT_PATH = BASE_DIR / "Kanit-Bold.ttf"

# ── 1. Generate หนูดี via FLUX ─────────────────────────────────────────
PROMPT = (
    "cute chubby cartoon chocolate Labrador Retriever, "
    "round pudgy body, happy sitting pose, tongue out smiling, "
    "looking at camera, white background, "
    "flat vector illustration kawaii style, full body, no text, "
    "high quality, clean lines, simple design"
)

print("Generating Nudee via FLUX.1-schnell...")
resp = requests.post(
    API_URL,
    headers={"Authorization": f"Bearer {HF_KEY}"},
    json={"inputs": PROMPT, "parameters": {"num_inference_steps": 4, "width": 512, "height": 512}},
    timeout=120,
)
resp.raise_for_status()
raw_img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
raw_img.save(OUT_DIR / "nudee_raw.png")
print(f"   saved nudee_raw.png ({raw_img.size})")

# ── 2. Remove background with rembg ───────────────────────────────────
try:
    from rembg import remove as rembg_remove
    print("Removing background with rembg...")
    nudee_nobg = rembg_remove(raw_img)
    nudee_nobg.save(OUT_DIR / "nudee_nobg.png")
    print("   saved nudee_nobg.png")
except ImportError:
    print("rembg not installed -- using raw image (white bg)")
    nudee_nobg = raw_img

# ── 3. Build Navbar Logo ───────────────────────────────────────────────
# Layout: [หนูดี icon 40px] [AIBiz Thailand text]
# Canvas: 200 x 48px, transparent background

LOGO_H = 52
ICON_SIZE = 44   # icon area

# Resize หนูดี to fit icon area (square crop from center)
iw, ih = nudee_nobg.size
crop_size = min(iw, ih)
left = (iw - crop_size) // 2
top  = max(0, (ih - crop_size) // 2 - ih // 8)  # slightly higher (face focus)
nudee_crop = nudee_nobg.crop((left, top, left + crop_size, top + crop_size))
nudee_icon = nudee_crop.resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)

# Load font — fallback to default if not found
try:
    font_brand  = ImageFont.truetype(str(FONT_PATH), 22)
    font_tagline = ImageFont.truetype(str(FONT_PATH), 11)
except Exception:
    font_brand  = ImageFont.load_default()
    font_tagline = ImageFont.load_default()

# Measure text
dummy = Image.new("RGBA", (1, 1))
dd = ImageDraw.Draw(dummy)
brand_bbox   = dd.textbbox((0, 0), "AIBiz Thailand", font=font_brand)
brand_w      = brand_bbox[2] - brand_bbox[0]
tagline_bbox = dd.textbbox((0, 0), "AI Automation", font=font_tagline)
tagline_w    = tagline_bbox[2] - tagline_bbox[0]

text_w = max(brand_w, tagline_w)
LOGO_W = ICON_SIZE + 10 + text_w + 8  # padding

logo = Image.new("RGBA", (LOGO_W, LOGO_H), (0, 0, 0, 0))

# Paste icon centered vertically
icon_y = (LOGO_H - ICON_SIZE) // 2
logo.paste(nudee_icon, (0, icon_y), nudee_icon)

draw = ImageDraw.Draw(logo)
text_x = ICON_SIZE + 10

# "AIBiz" white + "Thailand" gold  (on same line, two colors)
# Draw "AIBiz" in white
aibiz_bbox = dd.textbbox((0, 0), "AIBiz", font=font_brand)
aibiz_w = aibiz_bbox[2] - aibiz_bbox[0]
text_y_brand = (LOGO_H // 2) - 16
draw.text((text_x, text_y_brand), "AIBiz", font=font_brand, fill=(255, 255, 255, 255))
# Draw "Thailand" in gold right after
draw.text((text_x + aibiz_w + 4, text_y_brand), "Thailand", font=font_brand, fill=(201, 169, 110, 255))

# Tagline
tagline_y = text_y_brand + 26
draw.text((text_x, tagline_y), "AI Automation", font=font_tagline, fill=(180, 180, 180, 200))

logo.save(OUT_DIR / "navbar_logo.png")
print(f"   saved navbar_logo.png ({logo.size})")

# ── 4. Preview on dark background (simulate navbar) ───────────────────
nav_preview = Image.new("RGBA", (LOGO_W + 40, LOGO_H + 20), (26, 39, 68, 255))  # navy
nav_preview.paste(logo, (20, 10), logo)
nav_preview.save(OUT_DIR / "navbar_logo_preview.png")
print("   saved navbar_logo_preview.png (on navy bg)")

# ── 5. Favicon 64x64 and 32x32 ────────────────────────────────────────
for fav_size in (64, 32):
    fav = Image.new("RGBA", (fav_size, fav_size), (26, 39, 68, 255))  # navy bg
    icon_resized = nudee_icon.resize((fav_size - 4, fav_size - 4), Image.LANCZOS)
    fav.paste(icon_resized, (2, 2), icon_resized)
    fav.save(OUT_DIR / f"favicon_{fav_size}.png")
    print(f"   saved favicon_{fav_size}.png")

print("\n✅ Done! Files saved to:", OUT_DIR)
print("   nudee_raw.png         — ต้นฉบับจาก FLUX")
print("   nudee_nobg.png        — ตัด BG แล้ว")
print("   navbar_logo.png       — logo บน transparent")
print("   navbar_logo_preview.png — logo บน navy (simulate navbar)")
print("   favicon_64.png        — favicon preview")
print("   favicon_32.png        — favicon จริง")
