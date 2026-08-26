# -*- coding: utf-8 -*-
r"""ตรวจ encoding + โครงสร้าง + HTML tag balance ของบทเรียน Python 101 ทุก EP"""
import os, sys, django, re
from html.parser import HTMLParser

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_automate.settings")
django.setup()

from blog.models import Article

VOID = {"br", "img", "hr", "input", "meta", "link", "path", "rect", "circle",
        "line", "polygon", "text", "polyline", "ellipse", "use", "stop"}


class Balance(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append("ปิด </%s> โดยไม่มีเปิด" % tag)
        elif self.stack[-1] != tag:
            self.errors.append("ปิด </%s> แต่ค้างอยู่ที่ <%s>" % (tag, self.stack[-1]))
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass
        else:
            self.stack.pop()


rows = []
for a in Article.objects.filter(category__slug="python-101").order_by("slug"):
    c = a.content
    p = Balance()
    p.feed(c)
    unclosed = [t for t in p.stack]

    rows.append({
        "slug": a.slug,
        "id": a.pk,
        "status": a.status,
        "layout": a.layout,
        "chars": len(c),
        "thai": len(re.findall(r"[฀-๿]", c)),
        "qmark": "???" in c or "???" in a.title,
        "h2": len(re.findall(r"<h2>", c)),
        "code": len(re.findall(r"<pre><code>", c)),
        "callout": len(re.findall(r'class="callout', c)),
        "step": len(re.findall(r'class="step"', c)),
        "check": len(re.findall(r'class="checklist"', c)),
        "svg": len(re.findall(r"<svg", c)),
        "details": len(re.findall(r"<details", c)),
        "meta_ok": len(a.meta_description) <= 160 and len(a.meta_title) <= 70,
        "meta_len": (len(a.meta_title), len(a.meta_description)),
        "excerpt_len": len(a.excerpt),
        "errors": p.errors[:3],
        "unclosed": unclosed[:3],
    })

hdr = "%-16s %-4s %-7s %-6s %6s %5s %3s %5s %7s %4s %5s %3s %7s"
print(hdr % ("SLUG", "ID", "STATUS", "LAYOUT", "CHARS", "THAI", "H2", "CODE", "CALLOUT", "STEP", "CHECK", "SVG", "DETAILS"))
print("-" * 104)
for r in rows:
    print(hdr % (r["slug"], r["id"], r["status"], r["layout"], r["chars"], r["thai"],
                 r["h2"], r["code"], r["callout"], r["step"], r["check"], r["svg"], r["details"]))

print()
print("---- QA ----")
bad = False
for r in rows:
    issues = []
    if r["qmark"]:
        issues.append("พบ ??? (encoding พัง)")
    if r["status"] != "draft":
        issues.append("status ไม่ใช่ draft")
    if r["layout"] != "docs":
        issues.append("layout ไม่ใช่ docs")
    if not r["meta_ok"]:
        issues.append("meta ยาวเกิน %s" % (r["meta_len"],))
    if r["excerpt_len"] > 300:
        issues.append("excerpt ยาวเกิน 300 (%d)" % r["excerpt_len"])
    if r["errors"]:
        issues.append("tag ไม่สมดุล: %s" % r["errors"])
    if r["unclosed"]:
        issues.append("tag ไม่ได้ปิด: %s" % r["unclosed"])
    if issues:
        bad = True
        print("  %-16s %s" % (r["slug"], " | ".join(issues)))

if not bad:
    print("  ผ่านทุกข้อ — encoding สะอาด, draft ครบ, layout=docs ครบ, HTML tag สมดุล, meta ไม่เกินลิมิต")
