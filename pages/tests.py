"""เทสหน้าเว็บสาธารณะ — เน้นด่านกันบอทของฟอร์มติดต่อ

รันด้วย:
  $env:USE_MYSQL="False"; venv\\Scripts\\python.exe manage.py test pages
"""

from django.test import TestCase, override_settings
from django.urls import reverse

from pages.models import ContactLead


@override_settings(RECAPTCHA_ENABLED=False)
class ContactPageTests(TestCase):
    def test_หน้าติดต่อเปิดได้และมีช่องกับดัก(self):
        res = self.client.get(reverse("pages:contact"))
        self.assertEqual(res.status_code, 200)
        # ช่องกับดักต้องอยู่ในหน้าเสมอ ไม่งั้นบอทกรอกฟอร์มผ่านฉลุย
        self.assertContains(res, 'name="website"')

    def test_ส่งฟอร์มปกติแล้วได้_lead(self):
        res = self.client.post(reverse("pages:contact"), {
            "name": "คุณสมหญิง",
            "phone": "0891112222",
            "message": "อยากได้ระบบจองคิว",
            "consent_given": "true",
            "website": "",
        })
        self.assertRedirects(res, reverse("pages:contact"))
        self.assertEqual(ContactLead.objects.count(), 1)

    def test_บอทที่กรอกช่องกับดักไม่ได้ลงระบบ(self):
        self.client.post(reverse("pages:contact"), {
            "name": "Bot",
            "phone": "0000000000",
            "message": "buy cheap seo backlinks",
            "consent_given": "true",
            "website": "http://spam.example.com",
        })
        self.assertEqual(ContactLead.objects.count(), 0)
