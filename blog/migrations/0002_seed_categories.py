from django.db import migrations


CATEGORIES = [
    {"name": "Educational", "slug": "educational", "display_order": 1,
     "description": "บทความ how-to, tutorial, framework สำหรับให้ความรู้"},
    {"name": "Industry Insight", "slug": "insights", "display_order": 2,
     "description": "Trend, news, prediction ในวงการ AI"},
    {"name": "Case Study", "slug": "case-studies", "display_order": 3,
     "description": "เรื่องราวลูกค้าและ ROI ที่ได้จริง"},
    {"name": "Behind the Scenes", "slug": "behind-the-scenes", "display_order": 4,
     "description": "เบื้องหลังการทำงาน, brand, personality"},
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model("blog", "Category")
    for c in CATEGORIES:
        Category.objects.get_or_create(slug=c["slug"], defaults=c)


def unseed_categories(apps, schema_editor):
    Category = apps.get_model("blog", "Category")
    Category.objects.filter(slug__in=[c["slug"] for c in CATEGORIES]).delete()


class Migration(migrations.Migration):
    dependencies = [("blog", "0001_initial")]
    operations = [migrations.RunPython(seed_categories, unseed_categories)]
