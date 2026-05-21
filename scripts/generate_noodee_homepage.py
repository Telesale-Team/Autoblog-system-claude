# -*- coding: utf-8 -*-
"""
Generate Noodee Homepage Poses — 8 sections
Output: static/img/noodee/homepage/noodee_<section>.png (transparent BG)
"""
import os
import sys
import io
import time
import requests
from pathlib import Path
from PIL import Image

# ── Setup ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")

HF_KEY  = os.getenv("HUGGINGFACE_API_KEY", "")
API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
OUT_DIR = BASE_DIR / "static" / "img" / "noodee" / "homepage"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── FLUX Prompt Base ───────────────────────────────────────────────────────
BASE_PROMPT = (
    "cute chubby fat cartoon chocolate Labrador Retriever, "
    "round pudgy belly cream colored tummy patch, "
    "big round black nose with light brown freckles, "
    "big round glossy eyes white highlight, "
    "floppy ears, rosy pink cheeks both sides, "
    "flat vector illustration kawaii style, "
    "white background, full body, no text, "
    "clean outline, warm brown color, no accessories, "
)

# ── 8 Poses ────────────────────────────────────────────────────────────────
POSES = [
    {
        "name": "hero",
        "section": "1 - Hero",
        "pose": (
            "standing upright, one paw raised in cheerful wave, "
            "big happy smile tongue out, tail wagging up, "
            "excited welcoming pose, full of energy"
        ),
    },
    {
        "name": "pain",
        "section": "2 - Pain Points",
        "pose": (
            "sitting, head tilted slightly, one paw gently on cheek, "
            "concerned empathetic expression, eyebrows raised with worry, "
            "listening carefully pose"
        ),
    },
    {
        "name": "laptop",
        "section": "3 - How It Works",
        "pose": (
            "sitting in front of tiny laptop computer, paws on keyboard, "
            "excited bright eyes, focused working expression, "
            "enthusiastic helpful pose"
        ),
    },
    {
        "name": "present",
        "section": "4 - Use Cases",
        "pose": (
            "both arms and paws spread wide open in welcoming gesture, "
            "big proud smile, chest out, "
            "presenting pose like showing something great"
        ),
    },
    {
        "name": "confident",
        "section": "5 - ROI Teaser",
        "pose": (
            "sitting with arms and paws crossed confidently, "
            "knowing smile, slight nod, one eyebrow slightly raised, "
            "smug but friendly confident expression"
        ),
    },
    {
        "name": "menu",
        "section": "6 - Packages",
        "pose": (
            "holding up a small paper with both paws, "
            "proud smile, standing pose presenting offer, "
            "eager helpful expression, looking at viewer"
        ),
    },
    {
        "name": "trust",
        "section": "7 - Trust Signals",
        "pose": (
            "sitting straight with good posture, calm confident smile, "
            "chest forward, trustworthy professional expression, "
            "dignified but approachable, gentle warm eyes"
        ),
    },
    {
        "name": "run",
        "section": "8 - CTA Final",
        "pose": (
            "running forward toward viewer, tongue happily hanging out, "
            "ears flapping back, tail up wagging, "
            "enthusiastic come-with-me energy, dynamic motion pose"
        ),
    },
]


def generate_image(prompt: str, seed: int = 42) -> bytes:
    headers = {
        "Authorization": f"Bearer {HF_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "num_inference_steps": 4,
            "width": 512,
            "height": 512,
            "seed": seed,
        },
    }
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.content


def remove_bg(img_bytes: bytes) -> Image.Image:
    try:
        from rembg import remove
        out = remove(img_bytes)
        return Image.open(io.BytesIO(out)).convert("RGBA")
    except ImportError:
        print("  [warn] rembg ไม่ได้ติดตั้ง — บันทึกเป็น white bg แทน")
        return Image.open(io.BytesIO(img_bytes)).convert("RGBA")


def main():
    if not HF_KEY:
        print("ERROR: HUGGINGFACE_API_KEY ไม่พบใน .env")
        sys.exit(1)

    print(f"Output dir: {OUT_DIR}")
    print(f"Generating {len(POSES)} poses...\n")

    results = []
    for i, pose in enumerate(POSES, 1):
        out_path = OUT_DIR / f"noodee_{pose['name']}.png"

        if out_path.exists():
            print(f"[{i}/{len(POSES)}] SKIP {pose['name']} (มีอยู่แล้ว)")
            results.append({"name": pose["name"], "status": "skipped", "path": str(out_path)})
            continue

        prompt = BASE_PROMPT + pose["pose"]
        print(f"[{i}/{len(POSES)}] Generating: {pose['section']}...")
        print(f"  Prompt tail: {pose['pose'][:80]}...")

        try:
            img_bytes = generate_image(prompt, seed=100 + i)
            img = remove_bg(img_bytes)

            # Resize to 600x600 px
            img = img.resize((600, 600), Image.LANCZOS)
            img.save(out_path, "PNG", optimize=True)

            size_kb = out_path.stat().st_size // 1024
            print(f"  Saved: {out_path.name} ({size_kb} KB)")
            results.append({"name": pose["name"], "status": "ok", "path": str(out_path)})

        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({"name": pose["name"], "status": "error", "error": str(e)})

        # รอ 2 วินาทีระหว่าง request เพื่อไม่ให้ rate limit
        if i < len(POSES):
            time.sleep(2)

    print("\n=== สรุป ===")
    for r in results:
        icon = "OK" if r["status"] == "ok" else ("SKIP" if r["status"] == "skipped" else "ERR")
        print(f"  [{icon}] noodee_{r['name']}.png")

    ok = sum(1 for r in results if r["status"] == "ok")
    skip = sum(1 for r in results if r["status"] == "skipped")
    err = sum(1 for r in results if r["status"] == "error")
    print(f"\nสร้างใหม่: {ok} | ข้าม: {skip} | error: {err}")
    print(f"ทุกไฟล์อยู่ที่: {OUT_DIR}")


if __name__ == "__main__":
    main()
