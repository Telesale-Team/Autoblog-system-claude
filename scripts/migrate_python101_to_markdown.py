# -*- coding: utf-8 -*-
r"""
ย้ายบทเรียน Python 101 ทุก EP จาก HTML -> Markdown (content_format="markdown")

ทำอะไรบ้าง
1. แปลง content (HTML) เป็น Markdown + container syntax ด้วย html_to_docs_markdown
2. เซฟลง content_md แล้วตั้ง content_format="markdown"
   -> Article.save() จะ render กลับเป็น HTML ลง content ให้เอง
3. ตรวจ round-trip: เทียบ "เนื้อความล้วน" ก่อน/หลัง ต้องเหมือนเดิม ไม่มีอะไรหาย
4. เขียนไฟล์ .md ลง content_backlog/lessons/ เพื่อเก็บใน git

run: .\venv\Scripts\python.exe scripts\migrate_python101_to_markdown.py
"""
import os, sys, re, django, difflib

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_automate.settings")
django.setup()

from blog.models import Article
from html_to_docs_markdown import html_to_markdown

OUT_DIR = os.path.join(ROOT, "content_backlog", "lessons")
os.makedirs(OUT_DIR, exist_ok=True)


def plain(html):
    """ดึงเฉพาะเนื้อความ ตัด tag/svg ออก เพื่อเทียบว่าข้อมูลหายไหม"""
    h = re.sub(r"<svg.*?</svg>", " ", html, flags=re.S)
    h = re.sub(r"<[^>]+>", " ", h)
    h = h.replace("&nbsp;", " ").replace("&amp;", "&")
    h = h.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    return re.sub(r"\s+", " ", h).strip()


def svg_count(html):
    return len(re.findall(r"<svg", html))


articles = list(Article.objects.filter(category__slug="python-101").order_by("slug"))
print("พบบทเรียน %d ตอน\n" % len(articles))

problems = []

for a in articles:
    before_html = a.content
    before_text = plain(before_html)
    before_svg = svg_count(before_html)

    md = html_to_markdown(before_html)

    a.content_md = md
    a.content_format = "markdown"
    a.save()          # save() จะ render md -> content ให้เอง

    a.refresh_from_db()
    after_html = a.content
    after_text = plain(after_html)
    after_svg = svg_count(after_html)

    same = before_text == after_text
    ratio = difflib.SequenceMatcher(None, before_text, after_text).ratio()

    print("%-16s md %6d chars | html %6d -> %6d | svg %d -> %d | เนื้อความตรงกัน %s (%.2f%%)" % (
        a.slug, len(md), len(before_html), len(after_html),
        before_svg, after_svg, "ใช่" if same else "ไม่", ratio * 100))

    if not same:
        problems.append((a.slug, before_text, after_text))
    if before_svg != after_svg:
        problems.append((a.slug + " [svg หาย]", str(before_svg), str(after_svg)))

    # เก็บต้นฉบับ .md ลง git ด้วย
    path = os.path.join(OUT_DIR, a.slug + ".md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("<!-- ต้นฉบับ Markdown ของ Article #%d — แก้ที่นี่หรือใน Django admin ก็ได้ -->\n" % a.pk)
        f.write("<!-- title: %s -->\n\n" % a.title)
        f.write(md)

print()
if problems:
    print("!! พบความต่าง %d จุด — ตรวจก่อนใช้งาน" % len(problems))
    for slug, b, aft in problems[:3]:
        print("\n--- %s ---" % slug)
        sm = difflib.SequenceMatcher(None, b, aft)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != "equal":
                print("  %-8s เดิม: %r" % (tag, b[i1:i2][:120]))
                print("  %-8s ใหม่: %r" % ("", aft[j1:j2][:120]))
else:
    print("ผ่านทุกตอน — เนื้อความและ SVG ครบเท่าเดิมทุกตัวอักษร")

print("\nไฟล์ .md เก็บไว้ที่: content_backlog/lessons/")
