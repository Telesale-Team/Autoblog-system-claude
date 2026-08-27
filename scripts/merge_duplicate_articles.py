r"""ยุบบทความซ้ำ — เอาฉบับที่ตรวจแล้วไปทับฉบับที่ publish อยู่

พบเมื่อ 27 ส.ค. 2569 ว่า draft ที่เพิ่งตรวจคุณภาพไป ซ้ำกับบทความที่ publish แล้ว
  #12 (draft)  ซ้ำกับ  #8  (published 14 พ.ค. 69) — ชื่อเรื่องแทบเหมือนกันคำต่อคำ
  #15 (draft)  ซ้ำกับ  #38 (published 20 พ.ค. 69) — เรื่องตอบแชทช้าเหมือนกัน

เก็บฉบับที่ publish ไว้เพราะ slug ดีกว่าและมีอายุ SEO อยู่แล้ว
(slug ของ draft คือ "ai-1" กับ "5" ซึ่งใช้ไม่ได้) แล้วย้ายเนื้อหาที่แก้แล้วไปทับ

⚠️ DB ตัวนี้คือ production (192.168.1.2/peyo_agent) — แก้แล้วเห็นบนเว็บทันที
สคริปต์จึงสำรองของเดิมลงไฟล์ก่อนเสมอ

ใช้:  venv\Scripts\python.exe scripts/merge_duplicate_articles.py --backup-only
      venv\Scripts\python.exe scripts/merge_duplicate_articles.py --apply
"""

import argparse
import io
import json
import os
import sys
from datetime import date

import django

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_automate.settings")
django.setup()

from blog.models import Article  # noqa: E402
from marketing.models import ContentScore  # noqa: E402

# บทความที่แตะในรอบนี้ — สำรองทั้งหมดไม่ว่าจะแก้หรือแค่ตรวจ
TOUCHED = [8, 9, 11, 12, 14, 15, 18, 38]

# draft ที่ถูกยุบ -> บทความปลายทางที่ publish อยู่
MERGES = [
    {"draft": 12, "target": 8,  "md": "rev_article12_ecommerce_ai.md"},
    {"draft": 15, "target": 38, "md": "rev_article15_reply_speed.md"},
]

ASSETS = os.path.join(ROOT, "scripts", "article_assets")
BACKUP = os.path.join(ASSETS, "backup_articles_%s.json" % date.today().isoformat())


def backup():
    rows = []
    for pk in TOUCHED:
        a = Article.objects.filter(pk=pk).first()
        if a is None:
            continue
        rows.append({
            "id": a.pk, "title": a.title, "slug": a.slug, "status": a.status,
            "content_format": a.content_format, "content": a.content,
            "content_md": a.content_md, "excerpt": a.excerpt,
            "meta_title": a.meta_title, "meta_description": a.meta_description,
            "category_id": a.category_id, "author_id": a.author_id,
            "published_at": a.published_at.isoformat() if a.published_at else None,
        })
    io.open(BACKUP, "w", encoding="utf-8").write(
        json.dumps(rows, ensure_ascii=False, indent=2))
    print("สำรองบทความ %s ชิ้นไว้ที่ %s" % (len(rows), BACKUP))


def apply_merges():
    for spec in MERGES:
        draft = Article.objects.get(pk=spec["draft"])
        target = Article.objects.get(pk=spec["target"])
        md = io.open(os.path.join(ASSETS, spec["md"]), encoding="utf-8").read()

        # เนื้อหา โทน และ metadata มาจากฉบับที่ตรวจแล้ว
        target.content_format = "markdown"
        target.content_md = md
        target.content = ""          # กัน HTML เก่าค้างแล้วถูกหยิบไปแสดง
        target.excerpt = draft.excerpt
        target.meta_description = draft.meta_description
        target.author = draft.author
        target.category = draft.category
        # slug / title / published_at / status ของปลายทางคงเดิม — เหตุผลที่เก็บตัวนี้ไว้
        target.save()
        print("ทับเนื้อหา #%s <- #%s (%s ตัวอักษร)" % (target.pk, draft.pk, len(md)))

        # ย้ายใบตรวจคุณภาพไปผูกกับปลายทางก่อนลบ
        # ไม่งั้น CASCADE จะลบประวัติการตรวจ 2 รอบไปด้วย
        moved = ContentScore.objects.filter(article=draft).update(article=target)
        print("   ย้ายใบตรวจคุณภาพ %s ใบไปผูกกับ #%s" % (moved, target.pk))

        title = draft.title
        draft.delete()
        print("   ลบ draft #%s (%s) แล้ว" % (spec["draft"], title))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true", help="ลงมือจริง")
    p.add_argument("--backup-only", action="store_true", help="สำรองอย่างเดียว")
    args = p.parse_args()

    backup()
    if args.backup_only:
        return
    if not args.apply:
        print("ยังไม่ได้ลงมือ — ใส่ --apply เมื่อพร้อม")
        return
    apply_merges()


if __name__ == "__main__":
    main()
