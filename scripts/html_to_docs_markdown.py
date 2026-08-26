# -*- coding: utf-8 -*-
r"""
แปลง HTML บทความสาย docs กลับเป็น Markdown + container syntax (:::)

ใช้ครั้งเดียวตอนย้ายบทเรียนเดิมที่เขียนเป็น HTML มาเป็น Markdown
รองรับเฉพาะชุด component ที่เราใช้จริง (callout / analogy / step / checklist /
answer(details) / figure / pre-code / list / table-less) — ไม่ใช่ converter ทั่วไป

import แล้วเรียก html_to_markdown(html) ได้เลย
"""
import re
from html import unescape
from html.parser import HTMLParser

VOID = {"br", "img", "hr", "input", "meta", "link"}

CALLOUT_CLASS_TO_KIND = {
    "c-tip": "tip",
    "c-note": "note",
    "c-warn": "warn",
    "c-danger": "danger",
}


# ------------------------------------------------------------------ DOM
class Node:
    __slots__ = ("tag", "attrs", "children", "raw")

    def __init__(self, tag, attrs=None, raw=None):
        self.tag = tag
        self.attrs = dict(attrs or {})
        self.children = []
        self.raw = raw          # ใช้เก็บ <svg> ทั้งก้อนแบบดิบ

    def cls(self):
        return self.attrs.get("class", "").split()


class DomBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.root = Node("#root")
        self.stack = [self.root]
        self.svg_depth = 0
        self.svg_buf = []

    # --- svg: เก็บดิบทั้งก้อน ---
    def handle_starttag(self, tag, attrs):
        if self.svg_depth:
            self.svg_buf.append(self.get_starttag_text())
            if tag == "svg":
                self.svg_depth += 1
            return
        if tag == "svg":
            self.svg_depth = 1
            self.svg_buf = [self.get_starttag_text()]
            return
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        if self.svg_depth:
            self.svg_buf.append(self.get_starttag_text())
            return
        self.stack[-1].children.append(Node(tag, attrs))

    def handle_endtag(self, tag):
        if self.svg_depth:
            self.svg_buf.append("</%s>" % tag)
            if tag == "svg":
                self.svg_depth -= 1
                if self.svg_depth == 0:
                    self.stack[-1].children.append(Node("#svg", raw="".join(self.svg_buf)))
            return
        if tag in VOID:
            return
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if self.svg_depth:
            self.svg_buf.append(data)
            return
        self.stack[-1].children.append(data)

    def handle_entityref(self, name):
        self.handle_data("&%s;" % name)

    def handle_charref(self, name):
        self.handle_data("&#%s;" % name)


# --------------------------------------------------------------- inline
def inline(nodes):
    out = []
    for n in nodes:
        if isinstance(n, str):
            out.append(unescape(n))
        elif n.tag == "#svg":
            out.append(n.raw)
        elif n.tag in ("b", "strong"):
            out.append("**%s**" % inline(n.children).strip())
        elif n.tag in ("i", "em"):
            out.append("*%s*" % inline(n.children).strip())
        elif n.tag == "code":
            out.append("`%s`" % inline(n.children).strip())
        elif n.tag == "br":
            out.append("  \n")
        elif n.tag == "a":
            out.append("[%s](%s)" % (inline(n.children).strip(), n.attrs.get("href", "")))
        elif n.tag == "img":
            out.append("![%s](%s)" % (n.attrs.get("alt", ""), n.attrs.get("src", "")))
        elif n.tag == "span":
            out.append(inline(n.children))
        else:
            out.append(inline(n.children))
    return "".join(out)


def clean(text):
    """ยุบช่องว่างซ้ำ แต่รักษาการขึ้นบรรทัดที่มาจาก <br>"""
    parts = text.split("  \n")
    parts = [re.sub(r"[ \t\n]+", " ", p).strip() for p in parts]
    return "  \n".join(p for p in parts if p != "" or len(parts) == 1).strip()


def first_child(node, tag=None, css=None):
    for c in node.children:
        if isinstance(c, str):
            continue
        if tag and c.tag != tag:
            continue
        if css and css not in c.cls():
            continue
        return c
    return None


def lift_icon(node, css):
    """
    หา <span class="ico|emoji"> แล้วคืน (icon_node, ลูกที่เหลือ)

    รองรับ 2 โครงสร้าง:
      1. HTML ที่เขียนมือ   -> span เป็นลูกตรงของ div
      2. HTML ที่ render จาก Markdown -> span ถูก Markdown ห่อด้วย <p> อีกชั้น
    ข้อ 2 คือสิ่งที่ทำให้ convert ซ้ำรอบสองแล้วไอคอนหาย ถ้าไม่รองรับ
    """
    icon = None
    rest = []
    for c in node.children:
        if isinstance(c, str):
            rest.append(c)
            continue
        if icon is None and c.tag == "span" and css in c.cls():
            icon = c
            continue
        if icon is None and c.tag == "p":
            inner = [x for x in c.children if not (isinstance(x, str) and not x.strip())]
            if len(inner) == 1 and not isinstance(inner[0], str) \
                    and inner[0].tag == "span" and css in inner[0].cls():
                icon = inner[0]
                continue
        rest.append(c)
    return icon, rest


# ---------------------------------------------------------------- block
def blocks(nodes, depth=0):
    out = []
    for n in nodes:
        if isinstance(n, str):
            if n.strip():
                out.append(clean(n))
            continue

        tag = n.tag
        css = n.cls()

        if tag == "#svg":
            out.append(n.raw)

        elif tag in ("h1", "h2", "h3", "h4", "h5"):
            level = int(tag[1])
            out.append("#" * level + " " + clean(inline(n.children)))

        elif tag == "p":
            t = clean(inline(n.children))
            if t:
                out.append(t)

        elif tag == "ul":
            out.append("\n".join(
                "- " + clean(inline(li.children))
                for li in n.children
                if not isinstance(li, str) and li.tag == "li"))

        elif tag == "ol":
            items = [li for li in n.children if not isinstance(li, str) and li.tag == "li"]
            out.append("\n".join(
                "%d. %s" % (i + 1, clean(inline(li.children)))
                for i, li in enumerate(items)))

        elif tag == "pre":
            code = first_child(n, "code") or n
            text = "".join(
                unescape(c) if isinstance(c, str) else inline([c])
                for c in code.children
            )
            lang = ""
            for c in code.cls():
                if c.startswith("language-"):
                    lang = c[len("language-"):]
            out.append("```%s\n%s\n```" % (lang, text.strip("\n")))

        elif tag == "figure":
            cap = first_child(n, "figcaption")
            caption = clean(inline(cap.children)) if cap else ""
            body = [c for c in n.children
                    if isinstance(c, str) or c.tag != "figcaption"]
            out.append(":::figure %s\n%s\n:::" % (caption, "\n\n".join(blocks(body, depth + 1))))

        elif tag == "details":
            summ = first_child(n, "summary")
            label = clean(inline(summ.children)) if summ else "ดูเฉลย"
            body = [c for c in n.children
                    if isinstance(c, str) or c.tag != "summary"]
            out.append(":::answer %s\n%s\n:::" % (label, "\n\n".join(blocks(body, depth + 1))))

        elif tag == "div" and "callout" in css:
            kind = next((CALLOUT_CLASS_TO_KIND[c] for c in css if c in CALLOUT_CLASS_TO_KIND), "note")
            ico_node, kids = lift_icon(n, "ico")
            icon = clean(inline(ico_node.children)) if ico_node else ""
            # .callout__body คือ wrapper ที่ renderer สร้าง — แกะออกให้เหลือเนื้อหาจริง
            flat = []
            for c in kids:
                if not isinstance(c, str) and c.tag == "div" and "callout__body" in c.cls():
                    flat.extend(c.children)
                else:
                    flat.append(c)
            title, body_parts = "", []
            for c in flat:
                if isinstance(c, str):
                    continue
                if c.tag == "span" and "ttl" in c.cls() and not title:
                    title = clean(inline(c.children))
                    continue
                if c.tag == "p":
                    ttl = first_child(c, "span", "ttl")
                    if ttl is not None and not title:
                        title = clean(inline(ttl.children))
                        rest = [x for x in c.children if x is not ttl]
                        text = clean(inline(rest))
                        if text:
                            body_parts.append(text)
                        continue
                body_parts.extend(blocks([c], depth + 1))
            head = ":::%s[%s] %s" % (kind, icon, title) if icon else ":::%s %s" % (kind, title)
            out.append("%s\n%s\n:::" % (head.rstrip(), "\n\n".join(body_parts)))

        elif tag == "div" and "analogy" in css:
            emo_node, kids = lift_icon(n, "emoji")
            emoji = clean(inline(emo_node.children)) if emo_node else "💡"
            body = []
            for c in kids:
                if not isinstance(c, str) and c.tag == "div" and "analogy__body" in c.cls():
                    body.extend(c.children)
                else:
                    body.append(c)
            out.append(":::analogy %s\n%s\n:::" % (emoji, "\n\n".join(blocks(body, depth + 1))))

        elif tag == "div" and "step" in css:
            num_node = first_child(n, "div", "step__n")
            body_node = first_child(n, "div", "step__body")
            number = clean(inline(num_node.children)) if num_node else "1"
            heading, rest = "", []
            if body_node is not None:
                for c in body_node.children:
                    if not isinstance(c, str) and c.tag == "h3" and not heading:
                        heading = clean(inline(c.children))
                        continue
                    rest.append(c)
            out.append(":::step %s %s\n%s\n:::" % (
                number, heading, "\n\n".join(blocks(rest, depth + 1))))

        elif tag == "div" and "checklist" in css:
            out.append(":::checklist\n%s\n:::" % "\n\n".join(blocks(n.children, depth + 1)))

        elif tag in ("div", "section", "article", "blockquote"):
            out.extend(blocks(n.children, depth + 1))

        else:
            t = clean(inline([n]))
            if t:
                out.append(t)

    return [b for b in out if b.strip()]


def html_to_markdown(html):
    builder = DomBuilder()
    builder.feed(html)
    builder.close()
    md = "\n\n".join(blocks(builder.root.children))
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n"


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print(html_to_markdown(sys.stdin.read()))
