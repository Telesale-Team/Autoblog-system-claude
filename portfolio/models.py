from django.db import models
from django.urls import reverse
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field
from slugify import slugify


def slugify_th(value):
    return slugify(value, allow_unicode=False)


class CaseStudy(models.Model):
    INDUSTRY_CHOICES = [
        ("ecommerce", "ร้านค้า / E-Commerce"),
        ("clinic", "คลินิก / โรงพยาบาล"),
        ("hotel", "โรงแรม / รีสอร์ท"),
        ("b2b", "B2B / Lead Gen"),
        ("factory", "โรงงาน / โลจิสติกส์"),
        ("internal", "ทีมงานภายในองค์กร"),
        ("legal_finance", "กฎหมาย / การเงิน"),
        ("education", "โรงเรียน / สถาบัน"),
        ("other", "อื่น ๆ"),
    ]

    STATUS_CHOICES = [("draft", "Draft"), ("published", "Published")]

    project_title = models.CharField("ชื่อโปรเจกต์", max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True, allow_unicode=False)
    client_name = models.CharField("ชื่อลูกค้า", max_length=200, blank=True,
                                   help_text="เว้นว่างได้ถ้าลูกค้าไม่ให้เปิดเผย")
    industry = models.CharField("อุตสาหกรรม", max_length=30, choices=INDUSTRY_CHOICES)

    cover_image = models.ImageField("รูปปก", upload_to="portfolio/covers/%Y/%m/", blank=True, null=True)

    problem = models.TextField("ปัญหาเดิม")
    solution = CKEditor5Field("วิธีแก้", config_name="extends")
    result = models.TextField("ผลลัพธ์")

    roi_metric = models.CharField("ROI เด่น", max_length=120, blank=True,
                                  help_text="เช่น 'ลด workload 70%' หรือ 'เพิ่ม conversion 3 เท่า'")
    testimonial = models.TextField("Testimonial", blank=True)
    testimonial_by = models.CharField("ผู้พูด (ชื่อ + ตำแหน่ง)", max_length=200, blank=True)

    tech_stack = models.CharField("Tech stack", max_length=200, blank=True,
                                  help_text="เช่น 'LINE Messaging API, Claude, Django'")
    duration = models.CharField("ระยะเวลา", max_length=50, blank=True,
                                help_text="เช่น '2 สัปดาห์'")

    # SEO
    meta_title = models.CharField("Meta title", max_length=70, blank=True)
    meta_description = models.CharField("Meta description", max_length=160, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    is_featured = models.BooleanField("โชว์หน้าแรก", default=False)
    display_order = models.IntegerField(default=0)

    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Case Studies"
        ordering = ["display_order", "-published_at"]
        indexes = [
            models.Index(fields=["status", "-published_at"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.project_title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_th(self.project_title)[:220]
        if self.status == "published" and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("portfolio:detail", kwargs={"slug": self.slug})


class CaseStudyImage(models.Model):
    case_study = models.ForeignKey(CaseStudy, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="portfolio/gallery/%Y/%m/")
    caption = models.CharField(max_length=200, blank=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return f"{self.case_study.project_title} — image {self.id}"
