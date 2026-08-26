"""เทสคุมแผนพัฒนาระบบ

เทสชุดนี้ไม่ได้ตรวจว่าโค้ดทำงานถูก แต่ตรวจว่า "แผนไม่โกหก"
สิ่งที่พังบ่อยที่สุดคือคนลืมอัปเดตแผน ไม่ใช่โค้ดพัง
"""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from dashboard import roadmap as rm


class RoadmapDataTests(TestCase):
    """ตรวจความสมเหตุสมผลของข้อมูลในไฟล์แผน"""

    def test_exactly_one_phase_in_progress(self):
        # ถ้าทำหลายเฟสพร้อมกัน แปลว่าไม่มีใครรู้จริงว่าตอนนี้โฟกัสอะไร
        running = [p for p in rm.PHASES if p['status'] == rm.IN_PROGRESS]
        self.assertEqual(
            len(running), 1,
            'ต้องมีเฟสที่กำลังทำเพียงเฟสเดียว แต่ตอนนี้มี %d เฟส: %s'
            % (len(running), [p['no'] for p in running]),
        )

    def test_current_points_to_a_real_phase(self):
        self.assertIsNotNone(
            rm.current_phase(),
            'CURRENT ชี้ไปที่เฟส %s ซึ่งไม่มีอยู่ใน PHASES' % rm.CURRENT['phase'],
        )

    def test_current_phase_is_the_in_progress_one(self):
        phase = rm.current_phase()
        self.assertEqual(
            phase['status'], rm.IN_PROGRESS,
            'CURRENT ชี้ไปเฟส %s แต่เฟสนั้นสถานะเป็น %s ไม่ใช่ in_progress'
            % (phase['no'], phase['status']),
        )

    def test_phase_numbers_are_unique_and_ordered(self):
        numbers = [p['no'] for p in rm.PHASES]
        self.assertEqual(len(numbers), len(set(numbers)), 'เลขเฟสซ้ำกัน')
        self.assertEqual(numbers, sorted(numbers), 'เลขเฟสไม่เรียงลำดับ')

    def test_every_item_has_a_known_status(self):
        for phase in rm.PHASES:
            self.assertTrue(phase['items'], 'เฟส %s ไม่มีรายการงานเลย' % phase['no'])
            for item in phase['items']:
                self.assertIn(
                    item['status'], rm.STATUS_META,
                    'เฟส %s เรื่อง "%s" มีสถานะที่ไม่รู้จัก: %s'
                    % (phase['no'], item['name'], item['status']),
                )

    def test_blocked_items_must_explain_why(self):
        # เรื่องที่ติดรอตัดสินใจแต่ไม่บอกว่าติดอะไร = ไม่มีใครแก้ให้ได้
        for phase in rm.PHASES:
            for item in phase['items']:
                if item['status'] == rm.BLOCKED:
                    self.assertTrue(
                        item.get('note'),
                        'เฟส %s เรื่อง "%s" สถานะ blocked แต่ไม่ได้บอกเหตุผล'
                        % (phase['no'], item['name']),
                    )

    def test_todo_phase_has_no_completed_items(self):
        # เฟสที่ยังไม่เริ่มแต่มีงานเสร็จแล้ว แปลว่าสถานะเฟสผิด
        for phase in rm.PHASES:
            if phase['status'] != rm.TODO:
                continue
            done = [i for i in phase['items'] if i['status'] in rm.COMPLETED_STATUSES]
            self.assertFalse(
                done,
                'เฟส %s สถานะ todo แต่มีงานเสร็จแล้ว %d เรื่อง — ควรเป็น in_progress หรือ done'
                % (phase['no'], len(done)),
            )

    def test_progress_math_adds_up(self):
        p = rm.overall_progress()
        self.assertEqual(p['done'] + p['remaining'], p['total'])
        self.assertEqual(p['phases'], len(rm.PHASES))

    def test_decisions_have_code_and_date(self):
        for d in rm.DECISIONS:
            self.assertTrue(d.get('code'), 'มติไม่มีรหัสอ้างอิง')
            self.assertIsInstance(d.get('since'), date, 'มติ %s ไม่มีวันที่' % d.get('code'))

    def test_tech_debt_explains_why_and_has_owner(self):
        for t in rm.TECH_DEBT:
            self.assertTrue(t.get('why'), 'หนี้ทางเทคนิค "%s" ไม่ได้บอกเหตุผล' % t['topic'])
            self.assertTrue(t.get('owner'), 'หนี้ทางเทคนิค "%s" ไม่มีเจ้าภาพ' % t['topic'])


class RoadmapPageTests(TestCase):
    """หน้าแผนต้องเห็นได้เฉพาะ superuser และต้องไม่มีคอมเมนต์หลุดออกหน้าเว็บ"""

    def setUp(self):
        User = get_user_model()
        self.url = reverse('dashboard:roadmap')
        self.superuser = User.objects.create_superuser(
            username='rm_super', email='super@example.com', password='x')
        self.staff = User.objects.create_user(
            username='rm_staff', email='staff@example.com', password='x', is_staff=True)

    def test_superuser_sees_page(self):
        self.client.force_login(self.superuser)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ตอนนี้กำลังทำ')

    def test_staff_without_superuser_gets_404_not_403(self):
        # 404 เพราะคนที่ไม่ควรเห็น ไม่ควรรู้ด้วยซ้ำว่ามีหน้านี้อยู่
        self.client.force_login(self.staff)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_anonymous_is_redirected(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_no_comment_syntax_leaks_into_html(self):
        # {# #} ของ Django รองรับบรรทัดเดียว ถ้าคร่อมหลายบรรทัดจะถูกพิมพ์ออกหน้าเว็บทั้งก้อน
        self.client.force_login(self.superuser)
        html = self.client.get(self.url).content.decode('utf-8')
        for token in ('{#', '#}', '{% comment', 'endcomment'):
            self.assertNotIn(token, html, 'มีคอมเมนต์เทมเพลตหลุดออกหน้าเว็บ: %s' % token)

    def test_page_shows_remaining_count(self):
        self.client.force_login(self.superuser)
        response = self.client.get(self.url)
        self.assertContains(response, 'งานที่เหลือ')
        self.assertContains(response, 'ความคืบหน้ารวม')
