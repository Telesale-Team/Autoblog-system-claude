r"""ต่อรอบที่ 2 เข้ากับผลตรวจเดิม แทนที่จะสร้างผลตรวจใบใหม่

expert_panel.py --save สร้าง ContentScore ใบใหม่ทุกครั้ง ซึ่งเหมาะกับการตรวจครั้งแรก
แต่รอบที่ 2 ของบทความเดิมควรอยู่ในใบเดียวกัน เพราะ "เส้นทางการแก้คือของมีค่า"
ตามที่ SKILL.md ของ expert-panel-th เขียนไว้

ใช้:  venv\Scripts\python.exe scripts/expert_panel_round2.py <ไฟล์ JSON>
JSON ใช้รูปแบบเดียวกับ --save แต่เพิ่ม key "content_score_id"
"""

import json
import os
import sys

import django

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_automate.settings")
django.setup()

from marketing.models import ContentScore, ExpertScore  # noqa: E402


def main(path):
    payload = json.load(open(path, encoding="utf-8"))
    score = ContentScore.objects.get(pk=payload["content_score_id"])

    for rnd in payload["rounds"]:
        round_no = rnd["round_no"]
        # กันรันซ้ำ — รอบไหนบันทึกไปแล้วให้ข้าม
        if score.expert_scores.filter(round_no=round_no).exists():
            print("ข้ามรอบ %s ของใบตรวจ #%s (บันทึกไว้แล้ว)" % (round_no, score.pk))
            continue
        for e in rnd["experts"]:
            ExpertScore.objects.create(
                content_score=score,
                round_no=round_no,
                expert=e["expert"],
                lens=e.get("lens", ""),
                score=int(e["score"]),
                weight=float(e.get("weight", 1.0)),
                feedback=e.get("feedback", ""),
            )
        score.rounds = max(score.rounds, round_no)

    score.panel = "\n".join(e["expert"] for e in payload["rounds"][-1]["experts"])
    score.weaknesses = payload.get("weaknesses", score.weaknesses)
    score.slop_hits = payload.get("slop_hits", score.slop_hits)
    score.recalculate()
    score.save()

    print("ใบตรวจ #%s บทความ #%s -> %s คะแนน (%s) รวม %s รอบ"
          % (score.pk, score.article_id, score.aggregate, score.status, score.rounds))
    print("   ดูรายละเอียดที่ /owner/content-quality/%s/" % score.pk)


if __name__ == "__main__":
    main(sys.argv[1])
