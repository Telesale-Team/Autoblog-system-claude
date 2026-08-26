"""เทสหน้าคะแนนคุณภาพบทความ และประตูอนุมัติ

เรื่องที่ต้องกันให้แน่นที่สุด: ปุ่มอนุมัติที่ถูก disable ด้วย JS ถูกข้ามได้ง่ายมาก
ฝั่งเซิร์ฟเวอร์จึงต้องปฏิเสธเองไม่ว่าหน้าจอจะทำอะไร
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from blog.models import Article, Category
from marketing.models import ContentScore, ExpertScore, SlopPattern


class ContentQualityPageTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_superuser("cq_owner", "cq@example.com", "x")
        author = User.objects.create_user("cq_writer", "w@example.com", "x")
        category = Category.objects.create(name="ทดสอบ", slug="cq-cat")
        self.article = Article.objects.create(
            title="บทความทดสอบคุณภาพ", slug="cq-article", author=author,
            category=category, content="เนื้อหา", status="draft")

        self.passed = ContentScore.objects.create(
            article=self.article, aggregate=93, rounds=2,
            status=ContentScore.Status.PASSED, panel="ตัวตรวจ AI-slop\nผู้ตรวจ SEO")
        self.failed = ContentScore.objects.create(
            article=self.article, aggregate=71, rounds=3,
            status=ContentScore.Status.NEEDS_WORK)

        for rnd, val in ((1, 80), (2, 93)):
            ExpertScore.objects.create(
                content_score=self.passed, round_no=rnd, expert="ตัวตรวจ AI-slop",
                score=val, weight=ExpertScore.HUMANIZER_WEIGHT)
            ExpertScore.objects.create(
                content_score=self.passed, round_no=rnd, expert="ผู้ตรวจ SEO", score=val)

        self.client.force_login(self.owner)

    def test_list_page_renders(self):
        response = self.client.get(reverse("dashboard:content_quality"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["stat_awaiting"], 1)   # 93 แต่ยังไม่อนุมัติ
        self.assertEqual(response.context["stat_needs_work"], 1)
        self.assertEqual(response.context["stat_approved"], 0)

    def test_filters_narrow_the_list(self):
        url = reverse("dashboard:content_quality")
        self.assertEqual(len(self.client.get(url + "?f=awaiting").context["scores"]), 1)
        self.assertEqual(len(self.client.get(url + "?f=needs_work").context["scores"]), 1)
        self.assertEqual(len(self.client.get(url + "?f=approved").context["scores"]), 0)

    def test_detail_builds_round_trail_with_delta(self):
        url = reverse("dashboard:content_quality_detail", kwargs={"pk": self.passed.pk})
        rounds = self.client.get(url).context["rounds_data"]
        self.assertEqual(len(rounds), 2)
        self.assertEqual(rounds[0]["aggregate"], 80)
        self.assertEqual(rounds[1]["aggregate"], 93)
        self.assertEqual(rounds[1]["delta"], 13)      # เส้นทางการแก้ต้องอ่านออก
        self.assertEqual(rounds[0]["delta"], 0)       # รอบแรกไม่มีส่วนต่าง
        self.assertTrue(rounds[1]["is_last"])
        self.assertTrue(rounds[1]["passed"])

    def test_humanizer_sorted_first_in_each_round(self):
        url = reverse("dashboard:content_quality_detail", kwargs={"pk": self.passed.pk})
        first_round = self.client.get(url).context["rounds_data"][0]
        self.assertEqual(first_round["experts"][0].expert, "ตัวตรวจ AI-slop")

    def test_no_comment_syntax_leaks(self):
        for url in (reverse("dashboard:content_quality"),
                    reverse("dashboard:content_quality_detail", kwargs={"pk": self.passed.pk}),
                    reverse("dashboard:slop_patterns")):
            html = self.client.get(url).content.decode("utf-8")
            for token in ("{#", "#}", "{% comment", "endcomment"):
                self.assertNotIn(token, html, "คอมเมนต์หลุดที่ %s: %s" % (url, token))


class ApprovalViewTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_superuser("ap_owner", "a@example.com", "x")
        author = User.objects.create_user("ap_writer", "aw@example.com", "x")
        category = Category.objects.create(name="ทดสอบ", slug="ap-cat")
        self.article = Article.objects.create(
            title="บทความรออนุมัติ", slug="ap-article", author=author,
            category=category, content="เนื้อหา", status="draft")
        self.client.force_login(self.owner)

    def _score(self, aggregate):
        return ContentScore.objects.create(article=self.article, aggregate=aggregate, rounds=1)

    def _approve(self, score, **data):
        return self.client.post(
            reverse("dashboard:content_quality_approve", kwargs={"pk": score.pk}), data)

    def test_get_is_not_allowed(self):
        score = self._score(95)
        url = reverse("dashboard:content_quality_approve", kwargs={"pk": score.pk})
        self.assertEqual(self.client.get(url).status_code, 405)

    def test_passing_score_can_be_approved(self):
        score = self._score(95)
        self._approve(score)
        score.refresh_from_db()
        self.assertTrue(score.is_approved)
        self.assertEqual(score.approved_by, self.owner)

    def test_failing_score_rejected_without_override(self):
        # ปุ่มถูก disable ด้วย JS แต่ POST ตรงมาได้ ฝั่งเซิร์ฟเวอร์ต้องกันเอง
        score = self._score(71)
        self._approve(score)
        score.refresh_from_db()
        self.assertFalse(score.is_approved)

    def test_failing_score_approved_only_with_explicit_override(self):
        score = self._score(71)
        self._approve(score, override="1")
        score.refresh_from_db()
        self.assertTrue(score.is_approved)

    def test_approving_does_not_publish_the_article(self):
        # ประตูอนุมัติต้องไม่แตะสถานะบทความเอง เจ้าของกด publish เองเสมอ
        score = self._score(98)
        self._approve(score)
        self.article.refresh_from_db()
        self.assertEqual(self.article.status, "draft")

    def test_double_approve_keeps_first_approver(self):
        score = self._score(95)
        self._approve(score)
        score.refresh_from_db()
        first_time = score.approved_at
        self._approve(score)
        score.refresh_from_db()
        self.assertEqual(score.approved_at, first_time)


class SlopPatternViewTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_superuser("sp_owner", "s@example.com", "x")
        self.client.force_login(self.owner)
        self.existing = SlopPattern.objects.create(
            pattern="ครบวงจร", kind=SlopPattern.Kind.WORD, penalty=5,
            why="เคลมที่ตรวจไม่ได้", hit_count=12)

    def _payload(self, **overrides):
        data = {"pattern": "อย่างมีประสิทธิภาพ", "kind": "word", "penalty": "5",
                "why": "คำเติมที่ตัดแล้วความหมายเท่าเดิม", "fix": "ตัดทิ้ง",
                "example_bad": "", "example_ok": "", "is_active": "1"}
        data.update(overrides)
        return data

    def test_list_computes_hit_percentage(self):
        SlopPattern.objects.create(pattern="ยกระดับ", penalty=3, why="x", hit_count=6)
        patterns = self.client.get(reverse("dashboard:slop_patterns")).context["patterns"]
        self.assertEqual(patterns[0].hit_pct, 100)   # ตัวที่เจอบ่อยสุดเป็นฐาน
        self.assertEqual(patterns[1].hit_pct, 50)

    def test_create_new_pattern(self):
        self.client.post(reverse("dashboard:slop_pattern_save"), self._payload())
        self.assertTrue(SlopPattern.objects.filter(pattern="อย่างมีประสิทธิภาพ").exists())

    def test_bad_kind_is_rejected(self):
        self.client.post(reverse("dashboard:slop_pattern_save"),
                         self._payload(kind="ไม่มีชนิดนี้"))
        self.assertFalse(SlopPattern.objects.filter(pattern="อย่างมีประสิทธิภาพ").exists())

    def test_bad_penalty_is_rejected(self):
        self.client.post(reverse("dashboard:slop_pattern_save"),
                         self._payload(penalty="999"))
        self.assertFalse(SlopPattern.objects.filter(pattern="อย่างมีประสิทธิภาพ").exists())

    def test_empty_pattern_is_rejected(self):
        self.client.post(reverse("dashboard:slop_pattern_save"), self._payload(pattern="  "))
        self.assertEqual(SlopPattern.objects.count(), 1)

    def test_editing_never_touches_hit_count(self):
        # hit_count เป็นสถิติที่ระบบนับเอง คนแก้ไม่ได้ ไม่งั้นตัวเลขโกหก
        self.client.post(reverse("dashboard:slop_pattern_save"),
                         self._payload(pk=str(self.existing.pk), pattern="ครบวงจร",
                                       hit_count="0"))
        self.existing.refresh_from_db()
        self.assertEqual(self.existing.hit_count, 12)

    def test_unchecked_is_active_turns_off(self):
        payload = self._payload(pk=str(self.existing.pk), pattern="ครบวงจร")
        payload.pop("is_active")
        self.client.post(reverse("dashboard:slop_pattern_save"), payload)
        self.existing.refresh_from_db()
        self.assertFalse(self.existing.is_active)
