"""ใบงานประจำบทความ — รันซ้ำแล้วข้ามขั้นที่ทำเสร็จแล้ว

ปัญหาที่แก้: Article Workflow มี 4 ขั้น (เขียน → ภาพปก → diagram → ประกอบร่าง)
ถ้าพังที่ขั้น 3 เมื่อก่อนต้องเริ่มใหม่หมด รวมถึงยิง FLUX ซ้ำทั้งที่ปกเสร็จแล้ว
เปลืองโควตาและเวลาโดยไม่จำเป็น

ที่มาแนวคิด: PIPELINE_STEPS + start_point ใน AI-Content-Studio/pipeline.py
ของเขาเช็คจากไฟล์ที่มีอยู่จริงบนดิสก์ ซึ่งฉลาดกว่าเก็บสถานะแยก
เพราะไฟล์หายเมื่อไหร่สถานะก็ต้องกลับเป็นยังไม่ทำ — เราใช้วิธีเดียวกัน

ใช้:
    venv\\Scripts\\python.exe scripts/article_manifest.py status <slug>
    venv\\Scripts\\python.exe scripts/article_manifest.py done <slug> <ขั้น> [--note "..."]
    venv\\Scripts\\python.exe scripts/article_manifest.py reset <slug> <ขั้น>

ใบงานเก็บที่ scripts/article_assets/<slug>/manifest.json
"""

import argparse
import json
import os
import sys
from datetime import datetime

ASSETS_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "article_assets")

# ลำดับขั้นตาม feedback_article_workflow — ห้ามสลับลำดับ
STEPS = [
    ("write",    "เขียนบทความ",       "ต้นฉบับอยู่ใน DB เป็น draft แล้ว"),
    ("cover",    "ภาพปก",             "หนูดี + hook 3 บรรทัด + brand tag"),
    ("diagram",  "diagram ทุก H2",     "อย่างน้อยหัวข้อละ 1 รูป"),
    ("assemble", "ประกอบเข้าบทความ",   "ใส่ img ครบทุกจุดแล้ว"),
    ("score",    "ตรวจคุณภาพ",         "ผ่าน expert-panel-th แล้ว (ไม่บังคับ)"),
]
STEP_KEYS = [s[0] for s in STEPS]


def _path(slug):
    return os.path.join(ASSETS_ROOT, slug, "manifest.json")


def load(slug):
    path = _path(slug)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return {"slug": slug, "steps": {}, "created_at": datetime.now().isoformat(timespec="seconds")}


def save_manifest(slug, data):
    path = _path(slug)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    return path


def _files_for(slug, step):
    """ไฟล์จริงที่บอกว่าขั้นนั้นทำแล้ว — ความจริงอยู่ที่ดิสก์ ไม่ใช่ที่ manifest

    ถ้าใครลบไฟล์ทิ้ง สถานะต้องกลับเป็นยังไม่ทำเองโดยไม่ต้องมีใครไปแก้ manifest
    """
    folder = os.path.join(ASSETS_ROOT, slug)
    if not os.path.isdir(folder):
        return []
    names = os.listdir(folder)
    if step == "cover":
        return [n for n in names if n.endswith("-cover.webp")]
    if step == "diagram":
        return [n for n in names if n.endswith(".webp") and "-cover" not in n]
    return []


def status(slug):
    data = load(slug)
    rows = []
    for key, label, detail in STEPS:
        recorded = data["steps"].get(key, {})
        files = _files_for(slug, key)
        # ขั้นที่มีไฟล์เป็นหลักฐาน ให้ไฟล์ตัดสิน ขั้นที่ไม่มีไฟล์ใช้ที่บันทึกไว้
        if key in ("cover", "diagram"):
            done = bool(files)
        else:
            done = bool(recorded.get("done"))
        rows.append({
            "step": key, "label": label, "detail": detail,
            "done": done, "files": files,
            "at": recorded.get("at", ""), "note": recorded.get("note", ""),
        })

    next_step = next((r["step"] for r in rows if not r["done"]), None)
    return {
        "slug": slug,
        "manifest": _path(slug),
        "steps": rows,
        "done_count": sum(1 for r in rows if r["done"]),
        "total": len(rows),
        "next_step": next_step,
        "finished": next_step is None,
    }


def mark(slug, step, note="", done=True):
    if step not in STEP_KEYS:
        return {"error": "ไม่รู้จักขั้น '%s' — ที่มี: %s" % (step, ", ".join(STEP_KEYS))}
    data = load(slug)
    if done:
        data["steps"][step] = {
            "done": True,
            "at": datetime.now().isoformat(timespec="seconds"),
            "note": note,
        }
    else:
        data["steps"].pop(step, None)
    save_manifest(slug, data)
    return status(slug)


def _print_status(st):
    if st.get("error"):
        print(st["error"])
        return
    print("บทความ: %s   (%d/%d ขั้น)" % (st["slug"], st["done_count"], st["total"]))
    print("ใบงาน : %s" % st["manifest"])
    print()
    for r in st["steps"]:
        mark_ = "เสร็จ " if r["done"] else "ค้าง  "
        extra = ""
        if r["files"]:
            extra = "  [%d ไฟล์]" % len(r["files"])
        elif r["at"]:
            extra = "  [%s]" % r["at"]
        print("  %s %-18s %s%s" % (mark_, r["label"], r["detail"], extra))
        if r["note"]:
            print("         หมายเหตุ: %s" % r["note"])
    print()
    if st["finished"]:
        print("ครบทุกขั้นแล้ว — เหลือให้เจ้าของกด publish เอง")
    else:
        label = next(s[1] for s in STEPS if s[0] == st["next_step"])
        print("ทำต่อที่: %s (%s)" % (label, st["next_step"]))


def main():
    parser = argparse.ArgumentParser(description="ใบงานประจำบทความ")
    parser.add_argument("action", choices=["status", "done", "reset"])
    parser.add_argument("slug")
    parser.add_argument("step", nargs="?", default="")
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    if args.action == "status":
        _print_status(status(args.slug))
    elif args.action in ("done", "reset"):
        if not args.step:
            print("ต้องระบุขั้นด้วย — ที่มี: %s" % ", ".join(STEP_KEYS))
            return 1
        _print_status(mark(args.slug, args.step, args.note, done=args.action == "done"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
