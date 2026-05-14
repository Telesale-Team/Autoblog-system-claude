# AIBiz Thailand — Design System
**Version:** 1.0 | **Updated:** 2026-05-14
**Owner:** Frontend Designer (Agent #13)
**Single source of truth:** `static/css/main.css`

---

## Design Direction
**Option A: Tech Professional — Navy + Gold**
น่าเชื่อถือ, enterprise-grade, เหมาะกับ B2B SME ไทย

---

## Color Tokens

| Token | Value | ใช้กับ |
|-------|-------|--------|
| `--brand-navy` | `#1a2744` | Primary bg, Heading (light mode) |
| `--brand-blue` | `#2563eb` | btn-primary, link, focus ring |
| `--brand-blue-d` | `#1d4ed8` | Blue hover state |
| `--brand-gold` | `#c9a96e` | Accent: logo, navbar hover, highlight |
| `--brand-gold-d` | `#b8924f` | Gold hover state |
| `--brand-green` | `#10b981` | Success, positive metric |
| `--brand-dark` | `#0f172a` | Dark mode body background |
| `--brand-card` | `#111827` | Card background (dark mode) |
| `--brand-border` | `#1e2d4a` | Border color (dark mode) |

### Heading Colors (theme-aware)
| Mode | Color | Token |
|------|-------|-------|
| Dark mode | `#f1f5f9` | `--heading-dark-bg` |
| Light mode | `#1a2744` | `--heading-light-bg` (= brand-navy) |

### Rules การใช้สี
- ❌ ห้าม hardcode hex ใน template หรือ CSS นอก design tokens section นี้
- ✅ ใช้ CSS variable หรือ Bootstrap utility class เสมอ
- Gold (`--brand-gold`) ใช้เป็น **accent เท่านั้น** — ไม่ใช้กับ heading หรือ body text

---

## Typography

| Role | Font | Weight |
|------|------|--------|
| Body (TH) | Sarabun | 400 |
| Body emphasis | Sarabun | 600 |
| Heading display | Playfair Display | 700, 900 |
| Code | SF Mono / Cascadia Code / Consolas | 400 |

```css
/* ใช้ผ่าน variable */
font-family: var(--font-th);
font-family: var(--font-display);
```

---

## Button Hierarchy

แต่ละ section/page มี `btn-primary` ได้ **1 ปุ่มเท่านั้น**

| Class | ใช้เมื่อ | ตัวอย่าง |
|-------|---------|---------|
| `btn-primary` | CTA หลัก — action ที่ต้องการให้ user ทำ | "ปรึกษาฟรี", "ส่งข้อความ", "อ่านต่อ" (hero) |
| `btn-outline-secondary` | Secondary action, navigation | "ดูทั้งหมด", filter buttons |
| `btn-outline-primary` | CTA รองที่ยังต้องการ emphasis | เมื่อ btn-primary ถูกใช้แล้วในหน้า |
| `btn-gold` | Premium CTA พิเศษ (ใช้ประหยัด) | landing page hero เท่านั้น |
| `btn-sm` | Button ขนาดเล็ก ใน card หรือ sidebar | "อ่านต่อ" ใน article card |

---

## Component Standards

### Badge / Category
```html
<!-- ✅ ถูก: ใช้สีตาม category.color field -->
<span class="badge text-bg-{{ category.color }}">{{ category.name }}</span>

<!-- ❌ ผิด: text-primary ไม่ใช่ badge -->
<span class="text-primary">{{ category.name }}</span>
```

### Card
```html
<!-- Standard article card -->
<div class="border rounded overflow-hidden shadow-sm bg-body-tertiary">
  <img class="w-100 object-fit-cover" style="height:220px;" ...>
  <div class="p-4">
    <!-- content -->
  </div>
</div>
```

### CTA Section
```html
<!-- ✅ ถูก: ใช้ bg-dark class -->
<section class="cta-section bg-dark text-center py-5">
  <h2 class="text-white">...</h2>
  <a class="btn btn-primary btn-lg">...</a>
</section>

<!-- ❌ ผิด: gradient hardcode -->
<section style="background: linear-gradient(...)">
```

### Alert / Tip Box
```html
<!-- AI Tip box (ใน article) -->
<div class="ai-tip">
  <div class="ai-tip-label">💡 AI Tip</div>
  <p class="mb-0">เนื้อหา</p>
</div>
```
```css
/* CSS อยู่ใน main.css */
.ai-tip { border-left: 4px solid var(--brand-gold); ... }
```

---

## Layout Structure

### Page Template
```
base_public.html
├── <head> — CSS, fonts, meta
├── Theme Switcher (fixed bottom-right)
├── Navbar (pages/navbar.html)
├── {% block content %} ← เนื้อหาแต่ละหน้า
└── Footer (bg-black, 4 columns)
```

### Homepage Sections
```
Hero (image top, text bottom)
↓
2-Column Featured Cards
↓
Main Content (col-8) + Sidebar (col-4)
  └─ Sidebar: About, Recent, Categories, Tags
↓
Footer
```

### Breakpoints (Bootstrap 5)
| Name | Width | ใช้กับ |
|------|-------|--------|
| xs | < 576px | Mobile portrait |
| sm | ≥ 576px | Mobile landscape |
| md | ≥ 768px | Tablet |
| lg | ≥ 992px | Desktop |
| xl | ≥ 1200px | Large desktop |

---

## Dark / Light Mode Rules

1. ใช้ Bootstrap utility class เสมอ (`bg-body`, `bg-body-secondary`, `bg-dark`, `text-body-secondary`)
2. ห้าม hardcode สีที่แตกต่างกันระหว่าง dark/light — ให้ Bootstrap จัดการ
3. `bg-dark` และ `bg-black` ไม่ตาม theme — ใช้เมื่อต้องการ dark เสมอ (footer, CTA section)
4. `bg-body-secondary` = light gray (light) / dark gray (dark) — ใช้กับ sidebar, hero text bg

---

## Workflow การแก้ Design

```
1. Frontend Designer วิเคราะห์ + ออกแบบ
        ↓
2. Implement CSS/HTML
        ↓
3. ส่งให้ QA Agent ตรวจ (dark + light mode, mobile + desktop)
        ↓
4. QA pass → commit + push
        ↓
5. Deploy บน server (หนูดีสั่ง pull)
```

---

## ไฟล์สำคัญ

| ไฟล์ | หน้าที่ |
|------|--------|
| `static/css/main.css` | Design tokens + global styles (single source of truth) |
| `static/css/DESIGN_SYSTEM.md` | Document นี้ |
| `templates/base_public.html` | Base template ทุกหน้า public |
| `pages/templates/pages/navbar.html` | Navbar component |

---

## สิ่งที่ยังต้องทำ (Backlog)

- [ ] Theme Settings system จาก admin dashboard (ให้ admin เปลี่ยนสีได้)
- [x] Migrate hardcode hex ใน `main.css` เก่าให้ใช้ CSS variable
- [x] Fix button hierarchy ทุกหน้า (Priority 1)
- [x] Fix `blog/list.html` category badge
- [ ] WCAG AA contrast ratio audit ทุก component
