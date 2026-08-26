# -*- coding: utf-8 -*-
r"""ตรวจ encoding + โครงสร้าง EP0 หลังเขียนลง DB (กันปัญหา ??? จาก encoding)"""
import os, sys, django, re

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_automate.settings")
django.setup()

from blog.models import Article

a = Article.objects.get(slug="python-101-ep0")
c = a.content

print("title   :", a.title)
print("excerpt :", a.excerpt[:80], "...")
print("category:", a.category.name)
print("tags    :", ", ".join(t.name for t in a.tags.all()))
print("---- encoding check ----")
print("มี '???' ในเนื้อหา :", "???" in c or "???" in a.title)
thai = len(re.findall(r"[฀-๿]", c))
print("จำนวนอักขระไทย     :", thai)
print("---- structure ----")
print("h2 sections :", len(re.findall(r"<h2>", c)))
print("callout     :", len(re.findall(r'class="callout', c)))
print("step        :", len(re.findall(r'class="step"', c)))
print("checklist   :", len(re.findall(r'class="checklist"', c)))
print("analogy     :", len(re.findall(r'class="analogy"', c)))
print("figure/svg  :", len(re.findall(r"<figure>", c)), "/", len(re.findall(r"<svg", c)))
print("---- h2 list ----")
for h in re.findall(r"<h2>(.*?)</h2>", c):
    print("  -", h)
