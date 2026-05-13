from django.test import Client
from blog.models import Article

c = Client(SERVER_NAME="127.0.0.1")
r = c.get("/blog/", HTTP_HOST="127.0.0.1")
print("blog list:", r.status_code, "| OpenClaw mentions:", r.content.count(b"OpenClaw"))

r2 = c.get("/", HTTP_HOST="127.0.0.1")
print("home:", r2.status_code, "| has Insight section:", b"Insight" in r2.content)

for a in Article.objects.filter(status="published").order_by("-published_at"):
    r3 = c.get(f"/blog/{a.slug}/", HTTP_HOST="127.0.0.1")
    date = a.published_at.strftime("%Y-%m-%d")
    print(f"  {r3.status_code}  {date}  /blog/{a.slug}/  ({a.views_count} views)")
