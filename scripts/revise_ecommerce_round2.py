"""รอบที่ 2 ของ expert-panel — เขียนบทความ #12 และ #15 ใหม่ตามจุดอ่อนที่คณะกรรมการชี้

จุดอ่อนรอบที่ 1 ที่แก้ในสคริปต์นี้
  · เคสและตัวเลขที่ตรวจสอบไม่ได้  -> เปลี่ยนเป็นข้อมูลที่มีแหล่งอ้างอิงจริง
  · โทนและสรรพนามผิดโปรไฟล์ ecommerce -> เขียนด้วยเสียง "น้ำตาล" แทนตัวว่า "หนู"
  · ไม่พูดถึง Shopee / Lazada / TikTok Shop -> ใส่ข้อมูลตลาดจริงเข้าไป
  · ไม่มีการลงชื่อนามปากกา -> ลงชื่อท้ายบทความ

⚠️ สคริปต์นี้ไม่ publish อะไร บทความยังเป็น draft เหมือนเดิม
"""

import io
import os
import sys

import django

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_automate.settings")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from blog.models import Article, Category  # noqa: E402

SCRATCH = os.environ["REV_DIR"]

# บทความ -> ไฟล์ Markdown ที่เขียนใหม่ + excerpt + meta description
REVISIONS = {
    12: {
        "file": "rev12.md",
        "excerpt": "สสว. สำรวจ SME 2,704 ราย พบใช้ AI แค่ 11% แต่ UOB Business Outlook 2026 "
                   "บอกว่าเกิน 70% แล้ว ระยะห่างของสองตัวเลขนี้คือเวลาที่คู่แข่งใช้แซงร้านคุณ",
        "meta_description": "SME ไทยใช้ AI แค่ 11% (สสว. 2568) แต่ UOB 2026 บอกเกิน 70% "
                            "ดูข้อมูลตลาด Shopee Lazada TikTok Shop และวิธีวัดผลจริงก่อนเริ่มใช้ AI",
    },
    15: {
        "file": "rev15.md",
        "excerpt": "งาน HBR ปี 2011 พบว่าบริษัทตอบ lead ช้าเฉลี่ย 42 ชั่วโมง และ 23% ไม่ตอบเลย "
                   "ส่วน 'กฎ 5 นาที' ที่คนชอบอ้าง จริง ๆ มาจากงาน MIT/InsideSales ปี 2007",
        "meta_description": "ตอบแชทช้าเสียออเดอร์จริงไหม รวมตัวเลขจาก HBR 2011 และ MIT/InsideSales "
                            "2007 พร้อมข้อมูลตลาดแชทไทย LINE 56 ล้านคน และวิธีเริ่มใช้ AI Chatbot",
    },
}

WRITER_USERNAME = "warinya"      # วริญญา พาณิชยกุล — นักเขียนกลุ่ม e-commerce (นามปากกา น้ำตาล)
CATEGORY_SLUG = "ecommerce"


def main():
    author = get_user_model().objects.get(username=WRITER_USERNAME)
    category = Category.objects.get(slug=CATEGORY_SLUG)

    for pk, spec in REVISIONS.items():
        article = Article.objects.get(pk=pk)
        md = io.open(os.path.join(SCRATCH, spec["file"]), encoding="utf-8").read()

        article.content_format = "markdown"
        article.content_md = md
        article.excerpt = spec["excerpt"]
        article.meta_description = spec["meta_description"]
        article.author = author
        article.category = category
        # สถานะยังเป็น draft — เจ้าของกด publish เองเท่านั้น
        article.save()

        print("แก้แล้ว #%s  %s" % (pk, article.title))
        print("   ผู้เขียน %s | หมวด %s | ความยาว %s ตัวอักษร | สถานะ %s"
              % (author.get_full_name(), category.name, len(md), article.status))


if __name__ == "__main__":
    main()
