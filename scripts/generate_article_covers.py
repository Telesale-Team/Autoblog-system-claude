"""
Generate branded cover images — OpenClaw Thailand inspired layout.
1200x630 (OG standard) JPG saved to media/blog/covers/.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from blog.models import Article
from django.conf import settings
from django.core.files import File


COVERS = [
    {
        "slug": "openclaw-introduction-for-thai-sme",
        "title": "OpenClaw",
        "title_accent": "Intro",
        "subtitle": "AI Gateway แบบ Self-Hosted สำหรับ SME ไทย",
        "badge": "EDUCATIONAL",
        "badge_color": (16, 185, 129),     # green
        "features": "Self-Hosted • Multi-Channel • PDPA-Safe",
        "glow_color": (59, 130, 246),       # blue
        "arc_color": (16, 185, 129),        # green
    },
    {
        "slug": "5-reasons-ai-gateway-better-than-saas",
        "title": "5 Reasons",
        "title_accent": "Why",
        "subtitle": "AI Gateway บนเซิร์ฟเวอร์ตัวเอง ดีกว่า SaaS Chatbot",
        "badge": "INSIGHT",
        "badge_color": (139, 92, 246),      # purple
        "features": "Cost • Privacy • Multi-LLM • Customization • Scale",
        "glow_color": (139, 92, 246),
        "arc_color": (236, 72, 153),        # pink
    },
    {
        "slug": "openclaw-line-setup-in-5-minutes",
        "title": "LINE Setup",
        "title_accent": "5 min",
        "subtitle": "ตั้งค่า OpenClaw เชื่อม LINE ใน 5 นาที (ฉบับ SME)",
        "badge": "TUTORIAL",
        "badge_color": (245, 158, 11),      # orange
        "features": "Webhook • Agent • Memory • Live in Minutes",
        "glow_color": (52, 211, 153),       # green
        "arc_color": (59, 130, 246),        # blue
    },
]

W, H = 1200, 630
BG_TOP = (10, 15, 30)        # near-black navy
BG_BOTTOM = (15, 25, 50)     # slightly lighter navy


def find_font(size, bold=False):
    base = r"C:\Windows\Fonts"
    candidates = (
        [f"{base}\\segoeuib.ttf", f"{base}\\arialbd.ttf"] if bold
        else [f"{base}\\segoeui.ttf", f"{base}\\arial.ttf"]
    )
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def vertical_gradient(top, bottom):
    img = Image.new("RGB", (W, H), top)
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        c = (int(top[0] + (bottom[0] - top[0]) * t),
             int(top[1] + (bottom[1] - top[1]) * t),
             int(top[2] + (bottom[2] - top[2]) * t))
        for x in range(W):
            px[x, y] = c
    return img


def draw_glow(img, color, cx, cy, radius=300, alpha=0.35):
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color)
    layer = layer.filter(ImageFilter.GaussianBlur(120))
    return Image.blend(img, layer, alpha)


def draw_arcs(img, color):
    """Decorative arcs in bottom-right corner."""
    layer = img.copy()
    d = ImageDraw.Draw(layer)
    cx, cy = W + 40, H + 40
    for r in (480, 360, 260, 180):
        d.arc((cx - r, cy - r, cx + r, cy + r),
              start=180, end=270, fill=color, width=3)
    return Image.blend(img, layer, 0.55)


def draw_pill(d, x, y, text, color, font, padding_x=18, padding_y=8):
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    w = tw + padding_x * 2
    h = th + padding_y * 2
    # filled subtle background
    d.rounded_rectangle((x, y, x + w, y + h), radius=h // 2,
                        fill=(color[0] // 6, color[1] // 6, color[2] // 6),
                        outline=color, width=2)
    d.text((x + padding_x, y + padding_y - 2), text, font=font, fill=color)
    return w, h


def render_cover(spec, out_path):
    img = vertical_gradient(BG_TOP, BG_BOTTOM)

    # accent glows
    img = draw_glow(img, spec["glow_color"], W - 180, 120, radius=260, alpha=0.45)
    img = draw_glow(img, spec["arc_color"], W - 60, H - 80, radius=240, alpha=0.30)

    # decorative arcs bottom-right
    img = draw_arcs(img, spec["arc_color"])

    d = ImageDraw.Draw(img)

    # subtle dot grid (very faint)
    dot_layer = img.copy()
    dd = ImageDraw.Draw(dot_layer)
    for x in range(40, W, 40):
        for y in range(40, H, 40):
            dd.ellipse((x - 1, y - 1, x + 1, y + 1), fill=(255, 255, 255))
    img = Image.blend(img, dot_layer, 0.03)
    d = ImageDraw.Draw(img)

    # ── brand top-left ──
    f_brand = find_font(22, bold=True)
    d.text((52, 48), "AIBizThailand", font=f_brand, fill=(226, 232, 240))

    # subtle hairline under brand
    d.line([(52, 84), (200, 84)], fill=(71, 85, 105), width=1)

    # ── title block (left) ──
    f_title = find_font(96, bold=True)
    f_title_accent = find_font(96, bold=True)
    f_subtitle = find_font(28)

    title_x = 52
    title_y = 200

    # main title (white) + accent (colored) on same line
    d.text((title_x, title_y), spec["title"], font=f_title, fill="#ffffff")
    bbox = d.textbbox((0, 0), spec["title"], font=f_title)
    title_w = bbox[2] - bbox[0]
    d.text((title_x + title_w + 24, title_y),
           spec["title_accent"], font=f_title_accent, fill=spec["glow_color"])

    # subtitle
    d.text((title_x, title_y + 130), spec["subtitle"],
           font=f_subtitle, fill=(203, 213, 225))

    # ── status pill (bottom-left) ──
    f_pill = find_font(20, bold=True)
    draw_pill(d, 52, H - 130, spec["badge"], spec["badge_color"], f_pill)

    # ── feature keywords (bottom-left, below pill) ──
    f_features = find_font(20, bold=True)
    d.text((52, H - 70), spec["features"],
           font=f_features, fill=(148, 163, 184))

    # ── bottom-right small brand ──
    f_url = find_font(18)
    url = "aibiz.co.th"
    bbox = d.textbbox((0, 0), url, font=f_url)
    uw = bbox[2] - bbox[0]
    d.text((W - 52 - uw, H - 70), url, font=f_url, fill=(100, 116, 139))

    # accent thin line top
    d.rectangle([0, 0, W, 4], fill=spec["glow_color"])

    img.save(out_path, "JPEG", quality=88, optimize=True)


def main():
    base = Path(settings.MEDIA_ROOT) / "blog" / "covers" / "generated"
    base.mkdir(parents=True, exist_ok=True)

    for spec in COVERS:
        try:
            article = Article.objects.get(slug=spec["slug"])
        except Article.DoesNotExist:
            print(f"SKIP: {spec['slug']}")
            continue

        out_path = base / f"{spec['slug']}.jpg"
        render_cover(spec, out_path)

        with open(out_path, "rb") as f:
            article.cover_image.save(f"{spec['slug']}.jpg", File(f), save=True)
        print(f"OK: {spec['slug']} -> {article.cover_image.url}")


main()
