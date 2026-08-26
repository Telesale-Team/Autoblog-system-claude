# -*- coding: utf-8 -*-
"""
Markdown renderer สำหรับบทความสาย docs / บทเรียน

ทำไมต้องมีไฟล์นี้
-----------------
CKEditor เป็น WYSIWYG จึงลบแท็กที่ไม่รู้จักทิ้ง (callout, step, inline SVG หายหมด)
บทเรียนของเราเป็น "เนื้อหาที่มีโครงสร้าง" ไม่ใช่ข้อความไหลๆ เลยเขียนด้วย Markdown
แล้วแปลงเป็น HTML ตอนเซฟแทน — ต้นฉบับอยู่ใน Article.content_md
ผลลัพธ์ลง Article.content เหมือนเดิม ทำให้ template ไม่ต้องแก้อะไรเลย

Syntax ของ container (คลาสตรงกับ CSS ใน blog/templates/blog/detail.html)
-----------------------------------------------------------------------
    :::goal หัวข้อ           กล่องเป้าหมายของบทเรียน (callout c-tip ไอคอน 🎯)
    :::tip หัวข้อ            เคล็ดลับ            (callout c-tip)
    :::note หัวข้อ           ข้อมูลเสริม          (callout c-note)
    :::warn หัวข้อ           คำเตือน             (callout c-warn)
    :::danger หัวข้อ         กับดัก/ห้ามทำ        (callout c-danger)
    :::analogy 🍳            เปรียบเทียบให้เห็นภาพ
    :::step 1 หัวข้อ         สอนทีละขั้น
    :::checklist             เช็คลิสต์ (ข้างในใช้ - เป็น bullet)
    :::answer ดูเฉลยข้อ 1     กล่องเฉลยแบบพับซ่อน (details/summary)
    :::figure คำบรรยาย        รูป/ไดอะแกรม (วาง <svg> หรือ ![](url) ข้างใน)
    :::                      ปิด container (ปิดตัวในสุดที่เปิดค้างอยู่)

เปลี่ยนไอคอนเองได้ด้วยวงเล็บเหลี่ยม:  :::tip[💰] หัวข้อ
container ซ้อนกันได้ เช่น :::answer ข้างในมี code block หรือ :::warn ได้

หมายเหตุความปลอดภัย
-------------------
ผู้เขียนเป็น staff เท่านั้น และเราจงใจให้วาง raw HTML/SVG ได้
จึงไม่ sanitize output — ห้ามเปิดให้ user ทั่วไปเขียน content_md เด็ดขาด
"""
import re

import markdown

# ชนิด callout -> (คลาส CSS, ไอคอนเริ่มต้น)
CALLOUT_TYPES = {
    "goal":   ("callout c-tip", "🎯"),
    "tip":    ("callout c-tip", "💡"),
    "note":   ("callout c-note", "📌"),
    "warn":   ("callout c-warn", "⚠️"),
    "danger": ("callout c-danger", "🚫"),
}

# สไตล์ inline ของกล่องเฉลย (detail.html ยังไม่มี CSS สำหรับ <details>)
ANSWER_STYLE = (
    "background:#0f1626;border:1px solid #1f2937;border-radius:10px;"
    "padding:0.9rem 1.1rem;margin:0.9rem 0;"
)
ANSWER_SUMMARY_STYLE = "cursor:pointer;color:#c9a96e;font-weight:700;font-size:0.92rem;"

# :::ชนิด[ไอคอน] อาร์กิวเมนต์
OPEN_RE = re.compile(r"^:::([a-zA-Z]+)(?:\[([^\]]*)\])?[ \t]*(.*)$")
CLOSE_RE = re.compile(r"^:::[ \t]*$")

MD_EXTENSIONS = [
    "md_in_html",    # ให้ Markdown ทำงานข้างใน <div markdown="1">
    "fenced_code",   # ```python ... ```
    "tables",
    "attr_list",
    "sane_lists",
]


def _esc(text):
    """escape เฉพาะที่จำเป็นสำหรับใส่ใน attribute/ข้อความสั้นๆ"""
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _open_html(kind, icon, arg):
    """
    แปลงบรรทัด ::: เปิด เป็น HTML เปิด
    คืนค่า (บรรทัด HTML, จำนวนแท็กที่ต้องปิด, บรรทัด HTML ปิด)
    """
    # หมายเหตุ: div ชั้นนอกต้องมี markdown="1" ด้วย เพราะ md_in_html จะไม่มองลูก
    # ที่มี markdown attr ถ้าพ่อแม่เป็น raw HTML — ผลข้างเคียงคือ <span class="ico">
    # จะโดนห่อด้วย <p> ซึ่งจัดการไว้แล้วใน CSS (.callout > p:first-of-type)
    if kind in CALLOUT_TYPES:
        css, default_icon = CALLOUT_TYPES[kind]
        ico = icon or default_icon
        title = arg.strip()
        head = ['<div class="%s" markdown="1">' % css,
                '<span class="ico">%s</span>' % ico,
                '<div class="callout__body" markdown="1">']
        if title:
            head.append('<span class="ttl">%s</span>' % _esc(title))
            head.append("")
        return head, ["</div>", "</div>"]

    if kind == "analogy":
        ico = icon or (arg.strip() or "💡")
        return (['<div class="analogy" markdown="1">',
                 '<span class="emoji">%s</span>' % ico,
                 '<div class="analogy__body" markdown="1">'],
                ["</div>", "</div>"])

    if kind == "step":
        parts = arg.strip().split(None, 1)
        number = parts[0] if parts else "1"
        heading = parts[1] if len(parts) > 1 else ""
        head = ['<div class="step" markdown="1">',
                '<div class="step__n">%s</div>' % _esc(number),
                '<div class="step__body" markdown="1">']
        if heading:
            head.append("### " + heading)
            head.append("")
        return head, ["</div>", "</div>"]

    if kind == "checklist":
        return (['<div class="checklist" markdown="1">', ""], ["</div>"])

    if kind == "answer":
        label = arg.strip() or "ดูเฉลย"
        return (['<details style="%s" markdown="1">' % ANSWER_STYLE,
                 '<summary style="%s">%s</summary>' % (ANSWER_SUMMARY_STYLE, _esc(label)),
                 ""],
                ["</details>"])

    if kind == "figure":
        caption = arg.strip()
        close = ['<figcaption>%s</figcaption>' % _esc(caption)] if caption else []
        close.append("</figure>")
        # markdown="1" ใส่ตอน render (ดู _expand_containers) เพราะถ้าข้างในเป็น <svg>
        # Markdown จะห่อด้วย <p> โดยไม่จำเป็น
        return (['<figure __FIGMD__>', ""], close)

    # ชนิดที่ไม่รู้จัก — ปล่อยเป็น div ธรรมดา กันเนื้อหาหาย
    return (['<div class="%s" markdown="1">' % _esc(kind), ""], ["</div>"])


def _expand_containers(text):
    """แปลงบล็อก ::: ทั้งหมดเป็น HTML wrapper (รองรับการซ้อนกัน)"""
    out = []
    stack = []          # เก็บ list ของบรรทัดปิด
    fig_indexes = []    # ตำแหน่งบรรทัด <figure __FIGMD__> ที่รอเติม attribute
    in_fence = False

    for raw in text.replace("\r\n", "\n").split("\n"):
        # อย่าแตะอะไรที่อยู่ใน code fence
        if raw.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(raw)
            continue
        if in_fence:
            out.append(raw)
            continue

        if CLOSE_RE.match(raw):
            if stack:
                out.append("")
                out.extend(stack.pop())
                out.append("")
            else:
                out.append(raw)   # ::: เกินมา ปล่อยผ่านให้เห็นว่าผิด
            continue

        m = OPEN_RE.match(raw)
        if m and m.group(1).lower() in (
            set(CALLOUT_TYPES) | {"analogy", "step", "checklist", "answer", "figure"}
        ):
            kind = m.group(1).lower()
            icon = m.group(2)
            arg = m.group(3) or ""
            head, close = _open_html(kind, icon, arg)
            out.append("")
            for line in head:
                if line == "<figure __FIGMD__>":
                    fig_indexes.append(len(out))
                out.append(line)
            stack.append(close)
            continue

        out.append(raw)

    # ปิด container ที่ผู้เขียนลืมปิด
    while stack:
        out.append("")
        out.extend(stack.pop())

    # figure: ถ้าเนื้อหาข้างในขึ้นต้นด้วย <svg> ไม่ต้องใส่ markdown="1"
    # (ไม่งั้น Markdown จะห่อ svg ด้วย <p> โดยเปล่าประโยชน์)
    for idx in fig_indexes:
        body_starts_with_svg = False
        for line in out[idx + 1:]:
            if not line.strip():
                continue
            body_starts_with_svg = line.lstrip().startswith("<svg")
            break
        out[idx] = '<figure>' if body_starts_with_svg else '<figure markdown="1">'

    return "\n".join(out)


def render_docs_markdown(source):
    """Markdown (+ container syntax) -> HTML สำหรับเก็บลง Article.content"""
    if not source or not source.strip():
        return ""
    md = markdown.Markdown(extensions=MD_EXTENSIONS, output_format="html")
    return md.convert(_expand_containers(source))
