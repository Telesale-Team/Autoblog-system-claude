"""เครื่องมือของ skill expert-panel-th — เตรียมของก่อนตรวจ และบันทึกผลหลังตรวจ

คนให้คะแนนคือ LLM ไม่ใช่สคริปต์นี้ สคริปต์นี้ทำสองอย่างที่ LLM ทำเองไม่ดี:
  1. --prepare : ดึงบทความ + โปรไฟล์ segment + รายการ AI-slop จาก DB
                 และค้นหา slop แบบตรงตัวให้ (คนอ่านข้ามคำได้ เครื่องไม่ข้าม)
  2. --save    : บันทึกคะแนนทุกรอบลง DB คิดคะแนนถ่วงน้ำหนักให้ และนับ hit_count

ใช้:
    venv\\Scripts\\python.exe scripts/expert_panel.py --prepare 47 --segment beauty_wellness
    venv\\Scripts\\python.exe scripts/expert_panel.py --save 47 --json result.json

⚠️ สคริปต์นี้ไม่ publish อะไรทั้งสิ้น การเผยแพร่ต้องให้เจ้าของกดอนุมัติเองที่หน้าเว็บ
"""

import argparse
import json
import os
import sys


def _setup_django():
    import django
    from django.conf import settings
    if settings.configured:
        return
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root not in sys.path:
        sys.path.insert(0, root)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_automate.settings")
    django.setup()


def _article_text(article):
    """คืนเนื้อบทความเป็นข้อความล้วน ไม่ว่าจะเขียนมาแบบ Markdown หรือ HTML"""
    import re
    raw = article.content_md if article.content_format == "markdown" else article.content
    raw = raw or ""
    # ตัดแท็กและ container ออกให้เหลือแต่ถ้อยคำ เพราะเราตรวจ "การเขียน" ไม่ใช่ markup
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = re.sub(r":::\w*", " ", raw)
    return re.sub(r"[ \t]+", " ", raw)


def prepare(article_id, segment_key):
    _setup_django()
    from blog.models import Article
    from marketing.models import SlopPattern, SegmentProfile

    article = Article.objects.filter(pk=article_id).first()
    if article is None:
        return {"error": "ไม่พบบทความ id=%s" % article_id}

    text = _article_text(article)

    profile = None
    if segment_key:
        obj = SegmentProfile.objects.filter(key=segment_key, is_active=True).first()
        if obj is None:
            return {"error": "ไม่พบ segment '%s'" % segment_key}
        profile = obj.as_dict()

    # ค้นหา slop แบบตรงตัว — เครื่องไม่ข้ามคำเหมือนคนอ่าน
    patterns = SlopPattern.objects.filter(is_active=True)
    hits, catalog = [], []
    for p in patterns:
        catalog.append({
            "pattern": p.pattern, "kind": p.kind, "penalty": p.penalty,
            "why": p.why, "fix": p.fix,
        })
        count = text.count(p.pattern)
        if count:
            hits.append({
                "pattern": p.pattern, "count": count, "penalty": p.penalty,
                "total_penalty": p.penalty * count, "why": p.why, "fix": p.fix,
            })

    hits.sort(key=lambda h: -h["total_penalty"])
    return {
        "article": {
            "id": article.pk, "title": article.title, "status": article.status,
            "category": article.category.name if article.category_id else None,
            "word_count": len(text.split()),
            "content": text,
        },
        "segment": profile,
        "slop_catalog": catalog,
        "slop_hits": hits,
        "slop_penalty_total": sum(h["total_penalty"] for h in hits),
        "note": "คะแนนที่หักนี้เป็นข้อมูลให้กรรมการตัดสิน ไม่ได้หักออกจากคะแนนอัตโนมัติ",
    }


def save(article_id, payload):
    _setup_django()
    from django.utils import timezone
    from blog.models import Article
    from marketing.models import ContentScore, ExpertScore, SegmentProfile, SlopPattern

    article = Article.objects.filter(pk=article_id).first()
    if article is None:
        return {"error": "ไม่พบบทความ id=%s" % article_id}

    rounds = payload.get("rounds") or []
    if not rounds:
        return {"error": "ไม่มีข้อมูลรอบการให้คะแนนใน JSON"}

    segment = None
    if payload.get("segment"):
        segment = SegmentProfile.objects.filter(key=payload["segment"]).first()

    score = ContentScore.objects.create(
        article=article,
        segment=segment,
        rubric=payload.get("rubric", "content-quality"),
        rounds=max(r.get("round_no", 1) for r in rounds),
        panel="\n".join(
            e["expert"] for e in rounds[-1].get("experts", [])),
        weaknesses=payload.get("weaknesses", ""),
        slop_hits=payload.get("slop_hits", ""),
    )

    for rnd in rounds:
        for e in rnd.get("experts", []):
            ExpertScore.objects.create(
                content_score=score,
                round_no=rnd.get("round_no", 1),
                expert=e["expert"],
                lens=e.get("lens", ""),
                score=int(e.get("score", 0)),
                weight=float(e.get("weight", 1.0)),
                feedback=e.get("feedback", ""),
            )

    score.recalculate()
    score.save()

    # นับว่า slop ตัวไหนเป็นปัญหาจริง — ใช้จัดลำดับความสำคัญตอนสอนนักเขียน
    text = _article_text(article)
    for p in SlopPattern.objects.filter(is_active=True):
        n = text.count(p.pattern)
        if n:
            p.hit_count += n
            p.save(update_fields=["hit_count"])

    return {
        "content_score_id": score.pk,
        "aggregate": score.aggregate,
        "status": score.status,
        "rounds": score.rounds,
        "experts_saved": score.expert_scores.count(),
        "next": "ดูรายละเอียดและกดอนุมัติที่ /owner/content-quality/%s/" % score.pk,
        "reminder": "ห้าม publish เอง คะแนนผ่านไม่เท่ากับเจ้าของอนุมัติ",
    }


def main():
    parser = argparse.ArgumentParser(description="เครื่องมือของ skill expert-panel-th")
    parser.add_argument("--prepare", type=int, metavar="ARTICLE_ID",
                        help="ดึงบทความ โปรไฟล์ segment และรายการ AI-slop")
    parser.add_argument("--segment", default="", help="key ของกลุ่มลูกค้า")
    parser.add_argument("--save", type=int, metavar="ARTICLE_ID",
                        help="บันทึกผลการให้คะแนนลง DB")
    parser.add_argument("--json", help="ไฟล์ JSON ผลการให้คะแนน (ใช้กับ --save)")
    args = parser.parse_args()

    if args.prepare:
        result = prepare(args.prepare, args.segment)
    elif args.save:
        if not args.json:
            print("ต้องระบุ --json ด้วยตอนใช้ --save")
            return 1
        with open(args.json, encoding="utf-8") as fh:
            result = save(args.save, json.load(fh))
    else:
        parser.print_help()
        return 0

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get("error") else 0


if __name__ == "__main__":
    sys.exit(main())
