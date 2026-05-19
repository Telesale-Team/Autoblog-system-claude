from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.text import Truncator
from django_ckeditor_5.fields import CKEditor5Field
from slugify import slugify
import math


def slugify_th(value):
    return slugify(value, allow_unicode=False)


class Category(models.Model):
    COLOR_CHOICES = [
        ("primary", "Primary (น้ำเงิน)"),
        ("secondary", "Secondary (เทา)"),
        ("success", "Success (เขียว)"),
        ("danger", "Danger (แดง)"),
        ("warning", "Warning (เหลือง)"),
        ("info", "Info (ฟ้า)"),
        ("dark", "Dark (ดำ)"),
    ]

    name = models.CharField("ชื่อหมวด", max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True, allow_unicode=False)
    description = models.TextField("คำอธิบาย", blank=True)
    display_order = models.IntegerField(default=0)
    color = models.CharField("สี Badge", max_length=20, choices=COLOR_CHOICES, default="secondary")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_th(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:category", kwargs={"slug": self.slug})


class Tag(models.Model):
    name = models.CharField("ชื่อแท็ก", max_length=50, unique=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True, allow_unicode=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_th(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:tag", kwargs={"slug": self.slug})


class Article(models.Model):
    STATUS_CHOICES = [
        ("waiting",   "รอเขียน"),
        ("draft",     "Draft"),
        ("published", "Published"),
    ]

    title = models.CharField("หัวข้อ", max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True, allow_unicode=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="articles")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="articles")
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles")

    excerpt = models.TextField("สรุปย่อ (~160 chars)", max_length=300, blank=True)
    content = CKEditor5Field("เนื้อหา", config_name="extends")
    cover_image = models.ImageField("รูปปก (อัพโหลด)", upload_to="blog/covers/%Y/%m/", blank=True, null=True)
    cover_image_url = models.URLField("รูปปก (URL ภายนอก)", max_length=500, blank=True,
        help_text="ใส่ URL รูปจาก Unsplash หรือ CDN ภายนอก — ใช้แทนการอัพโหลดไฟล์ ถ้ากรอกทั้งคู่จะใช้ URL นี้")

    # SEO
    meta_title = models.CharField("Meta title (override)", max_length=70, blank=True)
    meta_description = models.CharField("Meta description", max_length=160, blank=True)
    og_image = models.ImageField("OG image", upload_to="blog/og/%Y/%m/", blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    backlog_ref = models.ForeignKey(
        "marketing.ContentBacklog", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="articles",
        verbose_name="มาจาก Backlog"
    )
    is_featured = models.BooleanField("โชว์หน้าแรก", default=False)
    views_count = models.PositiveIntegerField(default=0)

    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "-published_at"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        if self.status == "published" and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        """
        Auto-generate slug:
        1. ลอง python-slugify (transliterate บางภาษา)
        2. ลอง Django slugify (ASCII เท่านั้น)
        3. Fallback: article-{uuid8} ถ้าชื่อเป็นภาษาไทยล้วน
        ตรวจ uniqueness และเพิ่ม suffix -N ถ้าซ้ำ
        """
        from django.utils.text import slugify as django_slugify
        import uuid

        base = slugify_th(self.title)[:180]          # python-slugify
        if not base:
            base = django_slugify(self.title)[:180]  # Django slugify
        if not base:
            base = f"article-{uuid.uuid4().hex[:8]}" # Thai-only fallback

        slug = base
        i = 1
        while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base[:170]}-{i}"
            i += 1
        return slug

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"slug": self.slug})

    @property
    def reading_time(self):
        words = len(self.content.split())
        return max(1, math.ceil(words / 200))

    @property
    def display_meta_description(self):
        return self.meta_description or Truncator(self.excerpt or self.content).chars(160, truncate="…")

    @property
    def display_cover(self):
        """Return cover image URL — prefer external URL over uploaded file."""
        if self.cover_image_url:
            return self.cover_image_url
        if self.cover_image:
            return self.cover_image.url
        return ""

    @property
    def display_og_image(self):
        """OG image URL — prefer dedicated OG image > external URL > uploaded cover."""
        if self.og_image:
            return self.og_image.url
        return self.display_cover
