"""เทสหน้าโปรไฟล์กลุ่มลูกค้า (Segment Profile)

เน้นสองเรื่องที่พังแล้วเงียบ: การบันทึกค่าที่ไม่ถูกต้อง และคอมเมนต์เทมเพลตหลุดหน้าเว็บ
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from marketing.models import SegmentProfile


def make_profile(**overrides):
    data = dict(
        key="beauty_wellness",
        name="ร้านนวด / สปา",
        agent_slug="beauty-wellness-writer",
        pen_name="น้องข้าวเหนียว",
        pronoun="หนู",
        tone="Warm + Relatable",
        reader="เจ้าของร้านนวด",
        research="แหล่งที่หนึ่ง\n\nแหล่งที่สอง\n   \nแหล่งที่สาม",
        shape=SegmentProfile.Shape.ROUNDED,
        accent_secondary="#E8B4B8",
        icon_mood=SegmentProfile.IconMood.SOFT,
        prefer_diagram=SegmentProfile.DiagramType.STEPS,
        cover_pose=SegmentProfile.Pose.HAPPY,
        cover_mood=SegmentProfile.Mood.WARM,
        hook_style="คำถามที่ relate ได้",
    )
    data.update(overrides)
    return SegmentProfile.objects.create(**data)


class SegmentProfileModelTests(TestCase):

    def test_research_count_ignores_blank_lines(self):
        # ต้องนับแบบเดียวกับที่ as_dict() ตัด ไม่งั้นเลขบนหน้าจอไม่ตรงกับที่ script ได้ไป
        p = make_profile()
        self.assertEqual(p.research_count, 3)
        self.assertEqual(len(p.as_dict()["research"]), p.research_count)

    def test_as_dict_keys_match_skill_input(self):
        # ชื่อ key ต้องตรงกับ input ที่ SKILL.md ของ auto-diagram-generator
        # และ flux-cover-image ประกาศไว้ จะได้เสียบใช้ได้เลยไม่ต้องแปลงอีกชั้น
        d = make_profile().as_dict()
        self.assertEqual(
            set(d["diagram"]), {"shape", "accent_secondary", "icon_mood", "prefer_type"})
        self.assertEqual(
            set(d["cover"]), {"pose_category", "background_mood", "hook_style"})


class SegmentPageTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.staff = User.objects.create_user(
            username="seg_staff", email="s@example.com", password="x", is_staff=True)
        self.p = make_profile()
        self.list_url = reverse("dashboard:segments")
        self.edit_url = reverse("dashboard:segment_edit", kwargs={"key": self.p.key})

    def test_list_and_edit_pages_render(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(self.list_url).status_code, 200)
        self.assertEqual(self.client.get(self.edit_url).status_code, 200)

    def test_anonymous_is_redirected(self):
        self.assertEqual(self.client.get(self.list_url).status_code, 302)

    def test_unknown_key_returns_404(self):
        self.client.force_login(self.staff)
        url = reverse("dashboard:segment_edit", kwargs={"key": "not-a-segment"})
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_no_comment_syntax_leaks_into_html(self):
        self.client.force_login(self.staff)
        for url in (self.list_url, self.edit_url):
            html = self.client.get(url).content.decode("utf-8")
            for token in ("{#", "#}", "{% comment", "endcomment"):
                self.assertNotIn(token, html, "คอมเมนต์หลุดออกหน้าเว็บที่ %s: %s" % (url, token))

    def _payload(self, **overrides):
        data = {
            "tone": "โทนใหม่", "reader": "ผู้อ่านใหม่", "research": "แหล่งเดียว",
            "shape": "sharp", "accent_secondary": "#123abc", "icon_mood": "clean",
            "prefer_diagram": "concept", "cover_pose": "serious", "cover_mood": "clean",
            "hook_style": "hook ใหม่", "notes": "", "is_active": "on",
        }
        data.update(overrides)
        return data

    def test_valid_post_saves_and_uppercases_hex(self):
        self.client.force_login(self.staff)
        response = self.client.post(self.edit_url, self._payload())
        self.assertEqual(response.status_code, 302)
        self.p.refresh_from_db()
        self.assertEqual(self.p.tone, "โทนใหม่")
        self.assertEqual(self.p.accent_secondary, "#123ABC")

    def test_bad_choice_is_rejected(self):
        # POST ตรงมาโดยไม่ผ่านหน้าจอก็ต้องไม่ผ่าน radio ฝั่งหน้าจอกันได้ไม่หมด
        self.client.force_login(self.staff)
        response = self.client.post(self.edit_url, self._payload(shape="ไม่มีค่านี้"))
        self.assertEqual(response.status_code, 200)
        self.p.refresh_from_db()
        self.assertEqual(self.p.shape, SegmentProfile.Shape.ROUNDED)

    def test_bad_hex_is_rejected(self):
        self.client.force_login(self.staff)
        response = self.client.post(self.edit_url, self._payload(accent_secondary="red"))
        self.assertEqual(response.status_code, 200)
        self.p.refresh_from_db()
        self.assertEqual(self.p.accent_secondary, "#E8B4B8")

    def test_unchecked_is_active_turns_off(self):
        self.client.force_login(self.staff)
        payload = self._payload()
        payload.pop("is_active")
        self.client.post(self.edit_url, payload)
        self.p.refresh_from_db()
        self.assertFalse(self.p.is_active)


class SegmentApiTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.staff = User.objects.create_user(
            username="seg_api", email="a@example.com", password="x", is_staff=True)
        self.p = make_profile()

    def test_list_api_returns_only_active(self):
        make_profile(key="inactive_one", name="ปิดอยู่", is_active=False)
        self.client.force_login(self.staff)
        data = self.client.get(reverse("dashboard:api_segment_profiles")).json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["profiles"][0]["key"], "beauty_wellness")

    def test_detail_api_returns_thai_text_intact(self):
        self.client.force_login(self.staff)
        url = reverse("dashboard:api_segment_profile_detail", kwargs={"key": self.p.key})
        data = self.client.get(url).json()
        self.assertEqual(data["pen_name"], "น้องข้าวเหนียว")
        self.assertEqual(data["cover"]["pose_category"], "happy")
