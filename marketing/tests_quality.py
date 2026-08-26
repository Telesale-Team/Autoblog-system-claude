"""เทสระบบคุณภาพคอนเทนต์ — AI-slop, คะแนนถ่วงน้ำหนัก และประตูอนุมัติ

เรื่องที่ต้องคุมให้แน่นที่สุดคือ "คะแนนผ่าน ไม่เท่ากับ อนุมัติแล้ว"
ถ้าสองอย่างนี้หลอมเป็นอันเดียวเมื่อไหร่ กฎ draft-only จะพังทันที
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from blog.models import Article, Category
from marketing.models import ContentScore, ExpertScore, SegmentProfile, SlopPattern


def make_article(**overrides):
    User = get_user_model()
    author = User.objects.create_user(username="q_author", email="q@example.com", password="x")
    category = Category.objects.create(name="ทดสอบ", slug="test-cat")
    data = dict(
        title="บทความทดสอบ", slug="test-article", author=author, category=category,
        content="เนื้อหาทดสอบ", status="draft",
    )
    data.update(overrides)
    return Article.objects.create(**data)


class SlopPatternTests(TestCase):

    def test_detector_finds_pattern_in_thai_text(self):
        # จุดสำคัญ: ภาษาไทยไม่มีเว้นวรรคระหว่างคำ การจับต้องใช้ substring ไม่ใช่ split
        SlopPattern.objects.create(
            pattern="ในยุคดิจิทัลที่เปลี่ยนแปลงอย่างรวดเร็ว",
            penalty=10, why="วลีเปิดสำเร็จรูป")
        text = "ในยุคดิจิทัลที่เปลี่ยนแปลงอย่างรวดเร็ว ธุรกิจต้องปรับตัว"
        p = SlopPattern.objects.first()
        self.assertEqual(text.count(p.pattern), 1)

    def test_counts_repeated_occurrences(self):
        SlopPattern.objects.create(pattern="ครบวงจร", penalty=5, why="เคลมที่ตรวจไม่ได้")
        text = "ระบบครบวงจร บริการครบวงจร ดูแลครบวงจร"
        self.assertEqual(text.count("ครบวงจร"), 3)

    def test_ordering_puts_heaviest_first(self):
        SlopPattern.objects.create(pattern="เบา", penalty=3, why="x")
        SlopPattern.objects.create(pattern="หนัก", penalty=10, why="y")
        self.assertEqual(SlopPattern.objects.first().pattern, "หนัก")


class ContentScoreTests(TestCase):

    def setUp(self):
        self.article = make_article()
        self.score = ContentScore.objects.create(article=self.article, rounds=1)

    def _add(self, expert, score, weight=1.0, round_no=1):
        return ExpertScore.objects.create(
            content_score=self.score, round_no=round_no,
            expert=expert, score=score, weight=weight)

    def test_humanizer_weight_pulls_aggregate_down(self):
        # ตัวตรวจ AI-slop ถ่วง 1.5 เท่า — ถ้ามันให้คะแนนต่ำ ต้องดึงคะแนนรวมลงจริง
        self._add("ตัวตรวจ AI-slop", 60, ExpertScore.HUMANIZER_WEIGHT)
        self._add("ผู้ตรวจ SEO", 100)
        self._add("ผู้ตรวจโทน", 100)
        # (60*1.5 + 100 + 100) / 3.5 = 82.86 -> 83
        self.assertEqual(self.score.recalculate(), 83)
        self.assertEqual(self.score.status, ContentScore.Status.NEEDS_WORK)

    def test_all_high_scores_pass(self):
        self._add("ตัวตรวจ AI-slop", 95, ExpertScore.HUMANIZER_WEIGHT)
        self._add("ผู้ตรวจ SEO", 92)
        self.assertGreaterEqual(self.score.recalculate(), 90)
        self.assertEqual(self.score.status, ContentScore.Status.PASSED)

    def test_only_latest_round_counts_toward_aggregate(self):
        # รอบเก่าต้องเก็บไว้ดูเส้นทางการแก้ แต่ต้องไม่ถ่วงคะแนนรอบปัจจุบัน
        self._add("ผู้ตรวจ SEO", 40, round_no=1)
        self.score.rounds = 2
        self._add("ผู้ตรวจ SEO", 95, round_no=2)
        self.assertEqual(self.score.recalculate(), 95)
        self.assertEqual(self.score.expert_scores.count(), 2)

    def test_no_experts_gives_zero_not_crash(self):
        self.assertEqual(self.score.recalculate(), 0)


class ApprovalGateTests(TestCase):
    """คะแนนผ่าน กับ เจ้าของอนุมัติ ต้องแยกจากกันเสมอ"""

    def setUp(self):
        self.article = make_article()
        self.score = ContentScore.objects.create(article=self.article, aggregate=97, rounds=1)

    def test_high_score_alone_is_not_approval(self):
        self.assertTrue(self.score.is_passed)
        self.assertFalse(self.score.is_approved)

    def test_approval_requires_a_person_and_a_time(self):
        User = get_user_model()
        owner = User.objects.create_superuser("q_owner", "o@example.com", "x")
        self.score.approved_by = owner
        self.score.approved_at = timezone.now()
        self.score.save()
        self.assertTrue(self.score.is_approved)

    def test_failing_score_can_still_be_approved_deliberately(self):
        # เจ้าของมีสิทธิ์ข้ามเกณฑ์ แต่ต้องเป็นการกดเองเท่านั้น ระบบไม่ทำให้อัตโนมัติ
        User = get_user_model()
        owner = User.objects.create_superuser("q_owner2", "o2@example.com", "x")
        self.score.aggregate = 71
        self.score.approved_by = owner
        self.score.approved_at = timezone.now()
        self.score.save()
        self.assertFalse(self.score.is_passed)
        self.assertTrue(self.score.is_approved)

    def test_article_stays_draft_even_when_passed(self):
        # ระบบให้คะแนนต้องไม่แตะสถานะบทความเด็ดขาด
        self.article.refresh_from_db()
        self.assertEqual(self.article.status, "draft")
