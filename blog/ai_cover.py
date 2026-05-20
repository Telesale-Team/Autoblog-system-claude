# -*- coding: utf-8 -*-
"""
AI Cover Image Generator — น้องหนูดี Mascot System
สร้างภาพปกบทความ 4 องค์ประกอบ:
  1. น้องหนูดี cartoon pose ตาม category
  2. Background gradient สีประจำ category
  3. ข้อความภาษาไทย 4-5 คำ hook
  4. Auto-save เป็น cover_image ของบทความ
"""
import os
import re
import io
import requests
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile

# ── Config ─────────────────────────────────────────────────────────────
HF_KEY  = os.getenv("HUGGINGFACE_API_KEY", "")
API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

BASE_DIR  = Path(__file__).resolve().parent.parent
FONT_PATH = BASE_DIR / "Kanit-Bold.ttf"

# ── Category Config ────────────────────────────────────────────────────
CATEGORY_CONFIG = {
    "educational": {
        "bg_color":   "#0f1b35",  # Navy
        "text_color": "#ffffff",
        "accent":     "#c9a96e",  # Gold
        "pose":       "sitting upright reading an open book, wearing round glasses, academic pose",
        "bg_prompt":  "dark navy blue gradient background",
    },
    "insights": {
        "bg_color":   "#2d1b69",  # Purple
        "text_color": "#ffffff",
        "accent":     "#a78bfa",
        "pose":       "confident pose looking forward smiling, professional body language",
        "bg_prompt":  "deep purple gradient background",
    },
    "case-studies": {
        "bg_color":   "#064e3b",  # Green
        "text_color": "#ffffff",
        "accent":     "#4ade80",
        "pose":       "raising paw in celebration, excited happy expression",
        "bg_prompt":  "dark green gradient background",
    },
    "behind-the-scenes": {
        "bg_color":   "#431407",  # Orange/Brown
        "text_color": "#ffffff",
        "accent":     "#fb923c",
        "pose":       "peeking curiously from the side, playful expression",
        "bg_prompt":  "dark orange amber gradient background",
    },
    "openclaw": {
        "bg_color":   "#0a0f1a",  # Dark Navy
        "text_color": "#ffffff",
        "accent":     "#60a5fa",
        "pose":       "sitting in front of a glowing laptop computer, focused expression",
        "bg_prompt":  "very dark navy almost black gradient background with subtle blue glow",
    },
    "default": {
        "bg_color":   "#1a1a2e",  # Dark
        "text_color": "#ffffff",
        "accent":     "#c9a96e",
        "pose":       "happy sitting pose, tongue out, looking at camera",
        "bg_prompt":  "dark gradient background",
    },
}

# Fear-based articles (ชื่อไม่ใช่ category slug)
FEAR_CONFIG = {
    "bg_color":   "#3f0e0e",  # Deep Red
    "text_color": "#ffffff",
    "accent":     "#f87171",
    "pose":       "surprised wide-eyed expression, ears perked up, alert pose",
    "bg_prompt":  "deep dark red gradient background",
}

FEAR_KEYWORDS = ["แพ้", "ล้มเหลว", "หายไป", "เสียเปรียบ", "ช้า", "รีวิวแย่",
                 "ต้นทุน", "ลาออก", "ตัดสินใจ", "ไม่ปรับตัว"]


def get_config(article) -> dict:
    """เลือก config ตาม category และเนื้อหาบทความ"""
    title = article.title or ""
    # Fear-based override
    if any(kw in title for kw in FEAR_KEYWORDS):
        return FEAR_CONFIG
    # Category
    slug = article.category.slug if article.category else "default"
    return CATEGORY_CONFIG.get(slug, CATEGORY_CONFIG["default"])


def make_hook(title: str) -> str:
    """
    สร้าง hook text 2 บรรทัดจาก title
    - ตัดที่ขอบคำเสมอ ไม่ตัดกลางคำ
    - แต่ละบรรทัดไม่เกิน 12 ตัวอักษร
    - สูงสุด 2 บรรทัด
    """
    # ลบ prefix
    clean = re.sub(r'^\[.*?\]\s*', '', title)
    clean = re.sub(r'^EP\s*\d+:\s*', '', clean)
    text  = clean.split(" — ")[0].strip()

    words = text.split()
    if not words:
        return title[:12]

    lines   = []
    current = []

    for word in words:
        test = " ".join(current + [word])
        if not current or len(test) <= 12:
            # ยังพอใส่ได้ หรือบรรทัดว่างอยู่ (word ยาวแค่ไหนก็ต้องใส่)
            current.append(word)
        else:
            # บรรทัดเต็มแล้ว — เริ่มบรรทัดใหม่
            lines.append(" ".join(current))
            current = [word]
            if len(lines) == 2:
                break

    if current and len(lines) < 2:
        lines.append(" ".join(current))

    return "\n".join(lines[:2])


def build_flux_prompt(config: dict, hook: str) -> str:
    return (
        f"cute cartoon chocolate Labrador Retriever dog mascot, "
        f"{config['pose']}, "
        f"happy friendly expression, warm brown eyes, floppy ears, "
        f"flat vector illustration, kawaii cartoon style, "
        f"{config['bg_prompt']}, "
        f"blog thumbnail cover art composition, "
        f"character positioned on right side of frame, "
        f"no text, no watermark, clean design, high quality"
    )


def generate_flux_image(prompt: str, timeout: int = 60) -> bytes | None:
    """Generate ภาพด้วย FLUX.1-schnell"""
    if not HF_KEY:
        raise ValueError("HUGGINGFACE_API_KEY ไม่ได้ตั้งค่า")

    r = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {HF_KEY}"},
        json={
            "inputs": prompt,
            "parameters": {"width": 1200, "height": 675, "num_inference_steps": 4},
        },
        timeout=timeout,
    )
    if r.status_code == 200 and r.headers.get("content-type", "").startswith("image"):
        return r.content
    return None


def hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def darken(rgb: tuple, factor: float = 0.6) -> tuple:
    return tuple(int(c * factor) for c in rgb)


def add_text_overlay(img_bytes: bytes, hook: str, config: dict) -> bytes:
    """
    Layout แบบ YouTube thumbnail:
    - ซ้าย 55%: กล่องสี accent + ข้อความ 2 บรรทัด
    - ขวา 45%: น้องหนูดี (มาจาก FLUX แล้ว)
    - Diagonal stripe คั่นกลาง
    - Bottom-right: AIBiz Thailand tag
    """
    img  = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    W, H = img.size  # 1200×675
    draw = ImageDraw.Draw(img)

    # ── Colors ─────────────────────────────────────────────────────────
    accent_rgb = hex_to_rgb(config.get("accent", "#c9a96e"))
    dark_rgb   = darken(accent_rgb, 0.55)

    # ── Fonts ──────────────────────────────────────────────────────────
    lines   = [l for l in hook.split("\n") if l.strip()]
    max_len = max(len(l) for l in lines)
    fs      = 96 if max_len <= 6 else (80 if max_len <= 10 else 68)

    try:
        f_main  = ImageFont.truetype(str(FONT_PATH), fs)
        f_brand = ImageFont.truetype(str(FONT_PATH), 24)
    except Exception:
        f_main  = ImageFont.load_default()
        f_brand = f_main

    # ── Left color block (ซ้าย 55%) ───────────────────────────────────
    box_x2 = int(W * 0.56)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)

    # พื้นหลังกล่องซ้าย — สีเข้มกว่า accent เล็กน้อย
    ov_draw.rectangle([0, 0, box_x2, H], fill=(*dark_rgb, 210))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    # ── Diagonal stripe (orange divider) ──────────────────────────────
    stripe_w   = 38
    stripe_x   = box_x2
    stripe_pts = [
        (stripe_x - stripe_w, 0),
        (stripe_x + stripe_w, 0),
        (stripe_x + stripe_w * 3, H),
        (stripe_x, H),
    ]
    draw.polygon(stripe_pts, fill=(*accent_rgb, 230))

    # ── Text ───────────────────────────────────────────────────────────
    line_h  = fs + 16
    total_h = line_h * len(lines)
    x_txt   = 55
    y_start = (H - total_h) // 2 - 8

    for i, line in enumerate(lines):
        y = y_start + i * line_h
        # Shadow
        draw.text((x_txt + 4, y + 4), line, font=f_main, fill=(0, 0, 0, 180))
        # Line 1 — accent color, Line 2+ — white
        color = (*accent_rgb, 255) if i == 0 else (255, 255, 255, 255)
        draw.text((x_txt, y), line, font=f_main, fill=color)

    # ── Brand tag ──────────────────────────────────────────────────────
    tag_text = "AIBiz Thailand"
    tag_w, tag_h = 180, 36
    tag_x = W - tag_w - 20
    tag_y = H - tag_h - 20
    draw.rounded_rectangle([tag_x, tag_y, tag_x + tag_w, tag_y + tag_h],
                           radius=8, fill=(*accent_rgb, 200))
    draw.text((tag_x + 12, tag_y + 7), tag_text, font=f_brand, fill=(0, 0, 0, 220))

    # ── Export JPEG ────────────────────────────────────────────────────
    out = io.BytesIO()
    img.convert("RGB").save(out, format="JPEG", quality=93)
    return out.getvalue()


def generate_cover_for_article(article) -> bool:
    """
    Generate cover image สำหรับบทความ
    Return True ถ้าสำเร็จ
    """
    config  = get_config(article)
    hook    = make_hook(article.title)
    prompt  = build_flux_prompt(config, hook)

    img_bytes = generate_flux_image(prompt)
    if not img_bytes:
        return False

    # ใส่ text overlay
    final_bytes = add_text_overlay(img_bytes, hook, config)

    # Save ลง article
    fname = f"noodee-{article.slug[:40]}.jpg"
    article.cover_image.save(fname, ContentFile(final_bytes), save=False)
    article.cover_image_url = ""
    article.save()
    return True
