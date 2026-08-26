"""ตัวช่วยอ่านโปรไฟล์กลุ่มลูกค้า สำหรับ script ที่สร้าง diagram และภาพปก

ทำไมต้องมีไฟล์นี้: skill `auto-diagram-generator` กับ `flux-cover-image` เขียนสไตล์
ของตัวเองแยกกันมาตลอด บทความกลุ่มเดียวกันจึงได้ diagram กับปกที่ไม่ไปทางเดียวกัน
ตอนนี้ทั้งสองอ่านจาก `marketing.SegmentProfile` แถวเดียวกัน จบที่เดียว

ใช้จากใน script:
    from segment_profile import load_segment
    seg = load_segment("beauty_wellness")
    shape  = seg["diagram"]["shape"]              # rounded / soft / sharp
    accent = seg["diagram"]["accent_secondary"]   # สีรอง ห้ามใช้แทนสีแบรนด์
    pose   = seg["cover"]["pose_category"]

ใช้จาก command line (ดูค่าเร็ว ๆ):
    venv\\Scripts\\python.exe scripts/segment_profile.py beauty_wellness
    venv\\Scripts\\python.exe scripts/segment_profile.py --list

⚠️ สีแบรนด์กรม #0F172A + ทอง #C9A84C ห้ามเปลี่ยน — accent_secondary เป็นสีรองเท่านั้น
   ใช้ได้กับเส้นเน้น จุด ไอคอนเดี่ยว ห้ามเอาไปเป็นพื้นหลังหรือสีหัวข้อ
"""

import json
import os
import sys

# --- ค่าคงที่ของแบรนด์ — script ทุกตัวต้องใช้ชุดนี้ ห้าม hardcode ซ้ำ ---
BRAND_NAVY = "#0F172A"
BRAND_GOLD = "#C9A84C"
BRAND_TAG = "Noodee BootBiz"

# --- แปลงค่าใน DB เป็นค่าที่ Pillow / FLUX ใช้ได้ตรง ๆ ---
# เก็บไว้ที่นี่ที่เดียว เพราะทั้ง diagram และปกต้องแปลจากค่าเดียวกัน
CORNER_RADIUS = {"rounded": 24, "soft": 12, "sharp": 0}

ICON_STROKE = {"soft": 2, "clean": 2, "technical": 3, "energetic": 4}

MOOD_PROMPT = {
    "tech":  "clean modern tech environment, subtle circuit patterns, cool blue tones",
    "warm":  "soft warm interior light, gentle bokeh, cozy inviting atmosphere",
    "clean": "bright minimal studio background, lots of negative space, crisp and clinical",
    "dark":  "dramatic dark background, strong rim light, high contrast and moody",
}

POSE_PROMPT = {
    "thinking": "looking up thoughtfully with one paw near chin",
    "pointing": "pointing forward confidently with one paw",
    "happy":    "smiling brightly, ears up, cheerful and welcoming",
    "serious":  "sitting upright, calm and composed, professional expression",
    "reading":  "looking down at an open book with focused attention",
}


def _setup_django():
    """ตั้งค่า Django ให้พอเรียก ORM ได้ เรียกซ้ำได้ไม่พัง"""
    import django
    from django.conf import settings
    if settings.configured:
        return
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root not in sys.path:
        sys.path.insert(0, root)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_automate.settings")
    django.setup()


def load_segment(key):
    """คืนโปรไฟล์กลุ่มลูกค้าเป็น dict — รูปแบบเดียวกับ API /owner/api/segment-profiles/

    ถ้าหา key ไม่เจอจะ raise ทันที ไม่คืนค่า default เงียบ ๆ
    เพราะสไตล์ผิดกลุ่มมองไม่ออกจากรูป กว่าจะรู้ก็เผา FLUX ไปแล้ว
    """
    _setup_django()
    from marketing.models import SegmentProfile

    profile = SegmentProfile.objects.filter(key=key, is_active=True).first()
    if profile is None:
        available = list(
            SegmentProfile.objects.filter(is_active=True).values_list("key", flat=True))
        raise ValueError(
            "ไม่พบ segment '%s' — ที่มีอยู่: %s" % (key, ", ".join(available) or "(ยังไม่มีเลย)")
        )
    return profile.as_dict()


def list_segments():
    """คืนรายการ (key, ชื่อกลุ่ม, นามปากกา) ของทุกกลุ่มที่เปิดใช้อยู่"""
    _setup_django()
    from marketing.models import SegmentProfile
    return list(
        SegmentProfile.objects.filter(is_active=True)
        .values_list("key", "name", "pen_name")
    )


def diagram_style(seg):
    """แปลงโปรไฟล์เป็นค่าที่ script Pillow ใช้วาดได้เลย"""
    d = seg["diagram"]
    return {
        "bg": BRAND_NAVY,
        "primary": BRAND_GOLD,
        "accent": d["accent_secondary"],
        "corner_radius": CORNER_RADIUS.get(d["shape"], 12),
        "stroke_width": ICON_STROKE.get(d["icon_mood"], 2),
        "prefer_type": d["prefer_type"],
    }


def cover_prompt(seg, topic):
    """ประกอบ prompt พื้นหลังสำหรับ FLUX จากอารมณ์ที่กลุ่มนี้กำหนดไว้

    ไม่ใส่ตัวละครและตัวหนังสือใน prompt — หนูดีกับ hook วางทีหลังด้วย Pillow
    (ถ้าให้ FLUX วาดตัวหนังสือจะได้ตัวอักษรมั่ว และหนูดีจะผิดสเปก)
    """
    mood = MOOD_PROMPT.get(seg["cover"]["background_mood"], MOOD_PROMPT["clean"])
    return (
        "%s, background scene for a blog cover about %s, "
        "no text, no characters, no logos, "
        "navy blue and gold color palette, professional, 16:9"
        % (mood, topic)
    )


def nudee_pose_prompt(seg):
    """คำอธิบายท่าของหนูดีตามกลุ่ม — ใช้ต่อท้าย prompt base ใน character spec

    ⚠️ ยังต้องอ่าน memory `project_nudee_character_spec` และ `feedback_cover_pose_hook`
       ก่อนเสมอ ท่าต้องล้อกับ hook ที่เขียนจริง ไม่ใช่แค่ตามกลุ่ม
    """
    return POSE_PROMPT.get(seg["cover"]["pose_category"], POSE_PROMPT["thinking"])


def _main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0

    if argv[1] == "--list":
        for key, name, pen in list_segments():
            print("%-18s %-32s %s" % (key, name, pen))
        return 0

    try:
        seg = load_segment(argv[1])
    except ValueError as exc:
        print("ผิดพลาด: %s" % exc)
        return 1

    print(json.dumps(seg, ensure_ascii=False, indent=2))
    print("\n--- ค่าที่ Pillow ใช้ได้เลย ---")
    print(json.dumps(diagram_style(seg), ensure_ascii=False, indent=2))
    print("\n--- prompt พื้นหลังสำหรับ FLUX ---")
    print(cover_prompt(seg, "<หัวข้อบทความ>"))
    print("\n--- ท่าของหนูดี ---")
    print(nudee_pose_prompt(seg))
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
