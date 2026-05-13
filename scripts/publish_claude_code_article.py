"""
Publish the "Claude Code for Beginners" draft to the Django blog.
Run: ./venv/Scripts/python.exe manage.py shell < scripts/publish_claude_code_article.py
"""
import re
from pathlib import Path

import markdown
from django.contrib.auth import get_user_model

from blog.models import Article, Category, Tag

DRAFT_PATH = Path("content_briefs/how-to-use-claude-code-beginner-draft.md")

raw = DRAFT_PATH.read_text(encoding="utf-8")

# Strip YAML frontmatter
if raw.startswith("---"):
    _, _, rest = raw.partition("---")
    _, _, body = rest.partition("---")
    body = body.strip()
else:
    body = raw

# Drop the H1 line (Article.title is shown separately by the template)
lines = body.split("\n")
filtered = []
h1_dropped = False
for line in lines:
    if not h1_dropped and line.strip().startswith("# "):
        h1_dropped = True
        continue
    filtered.append(line)
body = "\n".join(filtered).strip()

html = markdown.markdown(
    body,
    extensions=["extra", "tables", "fenced_code", "sane_lists"],
)

User = get_user_model()
author = User.objects.get(username="admin")
category, _ = Category.objects.get_or_create(name="Educational")

slug = "how-to-use-claude-code-beginner"
title = "วิธีใช้ Claude Code สำหรับมือใหม่: เริ่มต้นใน 10 นาที"
excerpt = (
    "สอนใช้ Claude Code AI coding assistant ตั้งแต่ติดตั้งจนใช้งานได้จริง "
    "พร้อมตัวอย่างเขียนโค้ด แก้ bug และ automation สำหรับ dev ไทยมือใหม่ — เริ่มฟรี!"
)
meta_desc = excerpt[:160]

article, created = Article.objects.update_or_create(
    slug=slug,
    defaults={
        "title": title,
        "author": author,
        "category": category,
        "excerpt": excerpt,
        "content": html,
        "meta_title": title[:70],
        "meta_description": meta_desc,
        "status": "draft",
        "is_featured": False,
    },
)

for tag_name in ["Claude Code", "AI Coding", "Tutorial", "มือใหม่", "Anthropic"]:
    tag, _ = Tag.objects.get_or_create(name=tag_name)
    article.tags.add(tag)

action = "Created" if created else "Updated"
print(f"{action} Article id={article.id}")
print(f"Title: {article.title}")
print(f"Slug: {article.slug}")
print(f"Status: {article.status}")
print(f"URL: {article.get_absolute_url()}")
print(f"Word count (HTML): {len(html.split())}")
print(f"Tags: {[t.name for t in article.tags.all()]}")
