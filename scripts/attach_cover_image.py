"""
Download a remote cover image (e.g. Unsplash) and attach to a Django Article.

Usage (from project root):
  ./venv/Scripts/python.exe scripts/attach_cover_image.py \
      <article-slug> <image-url>

Example:
  ./venv/Scripts/python.exe scripts/attach_cover_image.py \
      how-to-use-claude-code-beginner \
      https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=1200
"""
import os
import sys
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI_automate.settings")
django.setup()

from django.core.files.base import ContentFile
from blog.models import Article


def download(url: str) -> tuple[bytes, str]:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (blog-publisher)"})
    with urlopen(req, timeout=30) as resp:
        data = resp.read()
        ctype = resp.headers.get("Content-Type", "")
    ext = "jpg"
    if "png" in ctype:
        ext = "png"
    elif "webp" in ctype:
        ext = "webp"
    elif "jpeg" in ctype or "jpg" in ctype:
        ext = "jpg"
    return data, ext


def main():
    if len(sys.argv) != 3:
        print("Usage: attach_cover_image.py <slug> <url>")
        sys.exit(1)

    slug, url = sys.argv[1], sys.argv[2]
    article = Article.objects.get(slug=slug)

    data, ext = download(url)
    filename = f"{slug}.{ext}"
    article.cover_image.save(filename, ContentFile(data), save=True)

    size_kb = len(data) // 1024
    print(f"OK: attached {filename} ({size_kb} KB) to article {article.id}")
    print(f"URL: {article.cover_image.url}")


if __name__ == "__main__":
    main()
