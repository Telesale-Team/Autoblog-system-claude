"""เทสคุมแผนการตลาดรายสัปดาห์ (playbook)

คู่กับ dashboard/tests_roadmap.py — ตรวจว่าไฟล์แผนไม่โกหกและหน้าเว็บไม่รั่วให้คนที่ไม่ควรเห็น
"""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from marketing import playbook as pb


class PlaybookDataTests(TestCase):
    """ตรวจความสมเหตุสมผลของข้อมูลในไฟล์แผน"""

    def test_every_channel_has_known_tracking_mode(self):
        for ch in pb.CHANNELS:
            self.assertIn(ch['tracking'], ('auto', 'manual'), 'channel %s tracking ไม่รู้จัก' % ch['key'])

    def test_auto_channels_declare_metric_key(self):
        for ch in pb.CHANNELS:
            if ch['tracking'] == 'auto':
                self.assertIn('metric_key', ch, 'channel %s เป็น auto แต่ไม่มี metric_key' % ch['key'])

    def test_manual_channels_declare_status(self):
        for ch in pb.CHANNELS:
            if ch['tracking'] == 'manual':
                self.assertIn(
                    ch.get('manual_status'), pb.STATUS_META,
                    'channel %s เป็น manual แต่ manual_status ไม่รู้จัก' % ch['key'],
                )

    def test_channel_keys_are_unique(self):
        keys = [c['key'] for c in pb.CHANNELS]
        self.assertEqual(len(keys), len(set(keys)), 'channel key ซ้ำกัน')

    def test_every_channel_has_note(self):
        # เหมือน roadmap: ต้องบอกที่มาและทำไมถึงตั้งเป้าเท่านี้ ไม่ใช่ตัวเลขลอยๆ
        for ch in pb.CHANNELS:
            self.assertTrue(ch.get('note'), 'channel %s ไม่มี note อธิบายที่มา' % ch['key'])

    def test_week_range_is_monday_to_sunday(self):
        # 2026-08-28 (ที่เขียนไฟล์นี้) เป็นวันศุกร์
        friday = date(2026, 8, 28)
        monday, sunday = pb.week_range(friday)
        self.assertEqual(monday.weekday(), 0)
        self.assertEqual(sunday.weekday(), 6)
        self.assertEqual((sunday - monday).days, 6)
        self.assertLessEqual(monday, friday)
        self.assertLessEqual(friday, sunday)

    def test_previous_week_is_exactly_one_week_before(self):
        today = date(2026, 8, 28)
        this_monday, _ = pb.week_range(today)
        prev_monday, prev_sunday = pb.previous_week_range(today)
        self.assertEqual((this_monday - prev_monday).days, 7)
        self.assertEqual((prev_sunday - prev_monday).days, 6)

    def test_build_channels_returns_status_for_every_channel(self):
        result = pb.build_channels(metrics={})
        self.assertEqual(len(result), len(pb.CHANNELS))
        for item in result:
            self.assertIn(item['status'], pb.STATUS_META)
            self.assertIsNotNone(item['meta'])

    def test_auto_channel_on_target_when_actual_meets_target(self):
        result = pb.build_channels(metrics={'seo_article': 2, 'seo_article_prev': 1})
        item = next(c for c in result if c['key'] == 'seo_article')
        self.assertEqual(item['status'], pb.ON_TARGET)
        self.assertEqual(item['trend_dir'], 'up')

    def test_auto_channel_not_started_when_zero(self):
        result = pb.build_channels(metrics={'seo_article': 0})
        item = next(c for c in result if c['key'] == 'seo_article')
        self.assertEqual(item['status'], pb.NOT_STARTED)

    def test_dynamic_target_channel_uses_metrics_target(self):
        result = pb.build_channels(metrics={
            'lead_follow_up': 3, 'lead_follow_up_target': 6, 'lead_follow_up_prev': 1,
        })
        item = next(c for c in result if c['key'] == 'lead_follow_up')
        self.assertEqual(item['target_resolved'], 6)
        self.assertEqual(item['status'], pb.PARTIAL)

    def test_channel_without_target_is_tracked_only(self):
        result = pb.build_channels(metrics={'expense_logging': 4})
        item = next(c for c in result if c['key'] == 'expense_logging')
        self.assertEqual(item['status'], pb.TRACKED)

    def test_weekly_summary_math_adds_up(self):
        summary = pb.weekly_summary(metrics={'leads_new': 5, 'leads_new_prev': 2})
        self.assertEqual(summary['total_channels'], len(pb.CHANNELS))
        self.assertLessEqual(summary['on_target'] + summary['not_started'], summary['total_channels'])
        self.assertEqual(summary['leads_new'], 5)


class PlaybookPageTests(TestCase):
    """หน้าแผนการตลาดต้องเห็นได้เฉพาะ superuser เหมือนหน้า roadmap"""

    def setUp(self):
        User = get_user_model()
        self.url = reverse('dashboard:playbook')
        self.superuser = User.objects.create_superuser(
            username='pb_super', email='pb_super@example.com', password='x')
        self.staff = User.objects.create_user(
            username='pb_staff', email='pb_staff@example.com', password='x', is_staff=True)

    def test_superuser_sees_page(self):
        self.client.force_login(self.superuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'สัปดาห์นี้')

    def test_staff_without_superuser_gets_404_not_403(self):
        self.client.force_login(self.staff)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_anonymous_is_redirected(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_no_comment_syntax_leaks_into_html(self):
        self.client.force_login(self.superuser)
        html = self.client.get(self.url).content.decode('utf-8')
        for token in ('{#', '#}', '{% comment', 'endcomment'):
            self.assertNotIn(token, html, 'มีคอมเมนต์เทมเพลตหลุดออกหน้าเว็บ: %s' % token)

    def test_page_shows_channel_names(self):
        self.client.force_login(self.superuser)
        response = self.client.get(self.url)
        for ch in pb.CHANNELS:
            self.assertContains(response, ch['name'])
