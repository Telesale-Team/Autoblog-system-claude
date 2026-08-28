"""เทสของงานเฟส 9 กลุ่ม ค. — หลังบ้านรับ lead จริงให้ได้

สิ่งที่เทสชุดนี้คุมไว้ (เรียงตามลำดับที่ลงมือ):
  1. กับดักบอทในฟอร์มหน้าเว็บทำงาน และไม่ขวางคนจริง
  2. ทำเครื่องหมายสแปมแล้ว lead รายนั้นหายจากทุกตัวเลขของหลังบ้าน
  3. บันทึก lead เองจากหลังบ้านได้ (lead จาก DM / LINE / คนแนะนำต่อ)
  4. บันทึกการติดต่อแล้วสถานะกับวันตามต่อขยับตาม
  5. ช่องทางครบ 8 ช่องตาม GTM ไม่งั้นคิดต้นทุนต่อ lead รายช่องทางไม่ได้

รันด้วย:
  $env:USE_MYSQL="False"; venv\\Scripts\\python.exe manage.py test dashboard.tests_leads
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from dashboard.forms import LeadForm
from pages.forms import ContactForm
from pages.models import ContactLead, LeadActivity


def make_lead(**kwargs):
    defaults = {
        "name": "ร้านกาแฟบ้านสวน",
        "email": "owner@example.com",
        "phone": "081-234-5678",
        "message": "อยากได้ระบบจองคิว",
    }
    defaults.update(kwargs)
    return ContactLead.objects.create(**defaults)


# ── 1. กับดักบอทในฟอร์มหน้าเว็บ ─────────────────────────────────────────────

@override_settings(RECAPTCHA_ENABLED=False)
class ContactFormHoneypotTests(TestCase):
    base_data = {
        "name": "คุณสมชาย",
        "email": "somchai@example.com",
        "phone": "0812345678",
        "message": "สนใจระบบจองคิว",
        "consent_given": "true",
    }

    def test_คนจริงกรอกผ่านได้(self):
        form = ContactForm(dict(self.base_data, website=""))
        self.assertTrue(form.is_valid(), form.errors)

    def test_บอทที่กรอกช่องกับดักถูกปฏิเสธ(self):
        form = ContactForm(dict(self.base_data, website="http://spam.example.com"))
        self.assertFalse(form.is_valid())
        self.assertIn("website", form.errors)

    def test_ไม่มีช่องยืนยันตัวตนเมื่อยังไม่ได้ตั้งกุญแจ(self):
        # ถ้าใส่ช่องนี้ทั้งที่ไม่มีกุญแจ ฟอร์มจะไม่ผ่านตลอดกาล ลูกค้าส่งข้อความไม่ได้
        self.assertNotIn("captcha", ContactForm().fields)

    def test_ฟอร์มบันทึกลงระบบได้ตามปกติ(self):
        form = ContactForm(dict(self.base_data, website=""))
        self.assertTrue(form.is_valid(), form.errors)
        lead = form.save(ip_address="1.2.3.4", source="landing")
        self.assertEqual(lead.source, "landing")
        self.assertTrue(lead.consent_given)
        self.assertIsNotNone(lead.consent_given_at)


@override_settings(RECAPTCHA_ENABLED=True,
                   RECAPTCHA_PUBLIC_KEY="test-public",
                   RECAPTCHA_PRIVATE_KEY="test-private")
class ContactFormCaptchaTests(TestCase):
    def test_มีช่องยืนยันตัวตนเมื่อตั้งกุญแจครบ(self):
        self.assertIn("captcha", ContactForm().fields)

    def test_ส่งฟอร์มโดยไม่ยืนยันตัวตนไม่ผ่าน(self):
        form = ContactForm({
            "name": "บอท", "email": "bot@example.com", "phone": "0000000000",
            "message": "spam", "consent_given": "true", "website": "",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("captcha", form.errors)


# ── 2. สแปมต้องหายจากทุกตัวเลข ──────────────────────────────────────────────

class SpamMarkingTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser("owner", "o@example.com", "pw")
        self.client.force_login(self.user)
        self.real = make_lead(name="ลูกค้าจริง")
        self.bot = make_lead(name="Bot Spam", email="bot@spam.example.com")

    def test_real_ตัดสแปมออก(self):
        self.bot.is_spam = True
        self.bot.save()
        self.assertEqual(list(ContactLead.objects.real()), [self.real])
        self.assertEqual(list(ContactLead.objects.spam()), [self.bot])

    def test_ปุ่มทำเครื่องหมายสแปมสลับค่าได้ทั้งสองทาง(self):
        url = reverse("dashboard:lead_toggle_spam", args=[self.bot.pk])
        self.client.post(url)
        self.bot.refresh_from_db()
        self.assertTrue(self.bot.is_spam)
        self.assertIsNotNone(self.bot.spam_marked_at)
        # ทำเครื่องหมายสแปมแล้วต้องออกจาก pipeline ด้วย ไม่ค้างเป็นงานที่ต้องทำ
        self.assertEqual(self.bot.status, "closed_lost")

        self.client.post(url)
        self.bot.refresh_from_db()
        self.assertFalse(self.bot.is_spam)
        self.assertIsNone(self.bot.spam_marked_at)

    def test_หน้ารายการซ่อนสแปมไว้เบื้องหลัง(self):
        self.bot.is_spam = True
        self.bot.save()
        res = self.client.get(reverse("dashboard:leads"))
        self.assertEqual(list(res.context["leads"]), [self.real])
        self.assertEqual(res.context["spam_count"], 1)

        res_spam = self.client.get(reverse("dashboard:leads") + "?status=spam")
        self.assertEqual(list(res_spam.context["leads"]), [self.bot])

    def test_ป้าย_lead_ใหม่_ไม่นับบอท(self):
        self.bot.is_spam = True
        self.bot.save()
        res = self.client.get(reverse("dashboard:leads"))
        self.assertEqual(res.context["new_count"], 1)


# ── 3. บันทึก lead เองจากหลังบ้าน ───────────────────────────────────────────

class ManualLeadTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser("owner", "o@example.com", "pw")
        self.client.force_login(self.user)

    def test_บันทึก_lead_จากการทัก_DM_ได้(self):
        res = self.client.post(reverse("dashboard:lead_new"), {
            "name": "คุณแนน ร้านเล็บ",
            "email": "", "phone": "089-999-9999", "company": "Nan Nail",
            "source": "cold_dm", "message": "ทักไปทาง IG",
            "status": "contacted", "deal_value": "",
            "next_follow_up": (timezone.localdate() + timedelta(days=3)).isoformat(),
            "notes": "", "consent_given": "on",
        })
        lead = ContactLead.objects.get(name="คุณแนน ร้านเล็บ")
        self.assertRedirects(res, reverse("dashboard:lead_detail", args=[lead.pk]))
        self.assertEqual(lead.source, "cold_dm")
        self.assertEqual(lead.created_by, self.user)
        # ไม่มีอีเมลก็บันทึกได้ ระบบเติมที่อยู่ภายในให้จากเบอร์โทร
        self.assertTrue(lead.email.endswith("@manual.aibizth.ai"))

    def test_หน้าเพิ่ม_lead_เปิดได้(self):
        res = self.client.get(reverse("dashboard:lead_new"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "เพิ่ม Lead เอง")

    def test_หน้ารายละเอียด_lead_เปิดได้(self):
        lead = make_lead()
        res = self.client.get(reverse("dashboard:lead_detail", args=[lead.pk]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, lead.name)

    def test_ไม่มีทั้งเบอร์และอีเมลบันทึกไม่ได้(self):
        form = LeadForm({"name": "ไม่รู้จัก", "source": "referral", "status": "new"})
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_ช่องทางที่เว็บกรอกเองไม่อยู่ในตัวเลือกตอนบันทึกมือ(self):
        values = [v for v, _ in LeadForm().fields["source"].choices]
        self.assertNotIn("landing", values)
        self.assertIn("line_oa", values)

    def test_แก้ไข_lead_ที่มาจากเว็บได้โดยไม่เสียช่องทางเดิม(self):
        lead = make_lead(source="landing")
        values = [v for v, _ in LeadForm(instance=lead).fields["source"].choices]
        self.assertIn("landing", values)


# ── 4. บันทึกการติดต่อ + วันตามต่อ ──────────────────────────────────────────

class LeadActivityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser("owner", "o@example.com", "pw")
        self.client.force_login(self.user)
        self.lead = make_lead()

    def _post_activity(self, **overrides):
        data = {
            "kind": "call",
            "note": "โทรคุยแล้ว เขาสนใจแพ็กกลาง ขอคิดดูก่อน",
            "occurred_at": timezone.localtime().strftime("%Y-%m-%dT%H:%M"),
            "next_follow_up": (timezone.localdate() + timedelta(days=5)).isoformat(),
        }
        data.update(overrides)
        return self.client.post(reverse("dashboard:lead_detail", args=[self.lead.pk]), data)

    def test_บันทึกการโทรแล้วสถานะขยับจาก_new_เป็น_contacted(self):
        self._post_activity()
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, "contacted")
        self.assertIsNotNone(self.lead.last_contacted_at)
        self.assertEqual(LeadActivity.objects.filter(lead=self.lead).count(), 1)

    def test_บันทึกการโทรตั้งวันตามต่อให้ด้วย(self):
        self._post_activity()
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.next_follow_up, timezone.localdate() + timedelta(days=5))
        self.assertEqual(self.lead.follow_up_state, "scheduled")

    def test_บันทึกภายในไม่นับว่าได้คุยกันแล้ว(self):
        self._post_activity(kind="note", note="ดูเว็บเขาแล้ว ร้านมี 2 สาขา")
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, "new")
        self.assertIsNone(self.lead.last_contacted_at)

    def test_ติ๊กปิดเคสแล้วไม่มีวันตามต่อ(self):
        self.lead.next_follow_up = timezone.localdate()
        self.lead.save()
        self._post_activity(clear_follow_up="on", next_follow_up="")
        self.lead.refresh_from_db()
        self.assertIsNone(self.lead.next_follow_up)
        self.assertEqual(self.lead.follow_up_state, "none")

    def test_ผู้บันทึกถูกเก็บไว้ด้วย(self):
        self._post_activity()
        self.assertEqual(LeadActivity.objects.get(lead=self.lead).created_by, self.user)


class FollowUpQueryTests(TestCase):
    def test_due_follow_up_เอาเฉพาะที่ถึงกำหนดและยังไม่ปิดดีล(self):
        today = timezone.localdate()
        overdue = make_lead(name="เลยกำหนด", next_follow_up=today - timedelta(days=2))
        due_today = make_lead(name="วันนี้", next_follow_up=today)
        make_lead(name="อนาคต", next_follow_up=today + timedelta(days=3))
        make_lead(name="ไม่ได้นัด")
        make_lead(name="ปิดไปแล้ว", next_follow_up=today, status="closed_won")
        make_lead(name="บอท", next_follow_up=today, is_spam=True)

        due = set(ContactLead.objects.due_follow_up().values_list("name", flat=True))
        self.assertEqual(due, {"เลยกำหนด", "วันนี้"})
        self.assertEqual(overdue.follow_up_state, "overdue")
        self.assertEqual(due_today.follow_up_state, "today")


# ── 5. ช่องทางครบ 8 ช่องตาม GTM ────────────────────────────────────────────

class SourceChoicesTests(TestCase):
    def test_มีครบทั้ง_8_ช่องทางของ_GTM(self):
        values = [v for v, _ in ContactLead.SOURCE_CHOICES]
        for channel in ["linkedin", "line_oa", "fb_group", "youtube",
                        "tiktok", "referral", "cold_dm", "google_ads"]:
            self.assertIn(channel, values, f"ขาดช่องทาง {channel} — คิด CAC รายช่องทางไม่ได้")

    def test_ช่องทางเดิมยังอยู่ครบ(self):
        # ข้อมูลเก่า 19 แถวเป็น source=landing ทั้งหมด ถ้าถอดออกจะกลายเป็นค่าที่อ่านไม่ออก
        values = [v for v, _ in ContactLead.SOURCE_CHOICES]
        for legacy in ["landing", "blog", "portfolio", "other"]:
            self.assertIn(legacy, values)
