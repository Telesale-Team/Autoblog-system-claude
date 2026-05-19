# Owner Dashboard — Design System Specification
**Version:** 1.0 | **Reference:** Phoenix v1.24.0 (prium.github.io/phoenix/v1.24.0/showcase.html)
**Scope:** /owner/* pages เท่านั้น (Public site ใช้ main.css + Navy/Gold brand แยกต่างหาก)

---

## 1. หลักการ (Principles)

1. **Shadow แทน Border** — Cards ใช้ shadow ไม่ใช้ border 1px
2. **Soft colors** — Status/Badge ใช้สี soft (opacity 0.1–0.15) ไม่ใช้สีเต็ม
3. **Uppercase labels** — Section labels, form labels, table headers → uppercase + letter-spacing
4. **Clickable rows** — Table row คลิกได้ทั้ง row ห้ามมี Actions column
5. **Consistent page structure** — ทุกหน้าใช้ settings-hero + scard pattern (settings.css)
6. **No hardcode** — ใช้ CSS variable เสมอ ห้าม hardcode hex

---

## 2. Color System

### Brand Tokens (Owner Dashboard)
```css
--app-primary:    #c9a96e;   /* Gold — buttons, active states, icons */
--app-secondary:  #b8924f;   /* Gold dark — hover */
--sidebar-bg:     #1a2744;   /* Navy — sidebar background */
```

### Semantic Colors (Phoenix-inspired)
```css
/* Success */
--color-success:        #00D27A;
--color-success-soft:   rgba(0, 210, 122, 0.12);
--color-success-text:   #009a58;

/* Warning */
--color-warning:        #F5803E;
--color-warning-soft:   rgba(245, 128, 62, 0.12);
--color-warning-text:   #c4631d;

/* Danger */
--color-danger:         #E63757;
--color-danger-soft:    rgba(230, 55, 87, 0.12);
--color-danger-text:    #c01236;

/* Info */
--color-info:           #2C7BE5;
--color-info-soft:      rgba(44, 123, 229, 0.12);
--color-info-text:      #1a5cbf;

/* Draft / Inactive */
--color-draft:          rgba(100, 116, 139, 0.12);
--color-draft-text:     #64748b;
```

### Page Background (Phoenix pattern)
```css
/* Light mode */
--page-bg:       #EDF2F9;   /* Phoenix soft gray-blue — ใส่ใน body */
--card-bg:       #FFFFFF;
--table-head-bg: #F9FAFD;

/* Dark mode */
--page-bg-dark:  #0B1727;
--card-bg-dark:  #132238;
--table-head-dark: #1e3a5f;
```

---

## 3. Card (scard)

### Pattern (Phoenix-inspired)
```css
.scard {
  background: var(--bs-body-bg);
  border-radius: 0.5rem;         /* 8px — ไม่ใช้ 0.75rem */
  box-shadow: 0 7px 14px 0 rgba(65,69,88,.08), 0 3px 6px 0 rgba(0,0,0,.05);
  border: none;                   /* ห้ามใช้ border */
  margin-bottom: 1.5rem;
}
.scard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--bs-border-color);
}
.scard-header-icon {
  width: 38px; height: 38px;
  border-radius: 0.5rem;
  background: linear-gradient(135deg, var(--app-primary), var(--app-secondary));
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.1rem; flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(201,169,110,.35);
}
.scard-body { padding: 1.5rem; }
```

---

## 4. Table

### Pattern
```css
.wc-table th {
  background: var(--table-head-bg);   /* Phoenix: #F9FAFD */
  padding: .6rem 1rem;
  font-size: .72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: var(--bs-secondary-color);
  border-bottom: 1px solid var(--bs-border-color);
  white-space: nowrap;
}
.wc-table td {
  padding: .75rem 1rem;
  border-bottom: 1px solid var(--bs-border-color);
  vertical-align: middle;
  font-size: .88rem;
}
/* ห้ามมี vertical border */
/* Row hover */
.wc-table tr:hover td { background: rgba(201,169,110,.04); }
```

### Clickable Row (กฎบังคับ)
```html
<!-- ✅ ถูก: row คลิกได้ -->
<tr style="cursor:pointer;" onclick="window.location='URL'">

<!-- ❌ ผิด: มี Actions column -->
<td><a href="...">แก้ไข</a></td>
```
**ถ้ามี element คลิกแยก (เช่น status badge) ต้องใส่ `event.stopPropagation()`**

---

## 5. Status Badge

### Pattern (Soft color)
```css
/* ✅ ถูก: Soft color */
.badge-published { background: rgba(0,210,122,.12); color: #009a58; border: 1px solid rgba(0,210,122,.25); }
.badge-draft     { background: rgba(100,116,139,.12); color: #64748b; border: 1px solid rgba(100,116,139,.2); }
.badge-warning   { background: rgba(245,128,62,.12); color: #c4631d; border: 1px solid rgba(245,128,62,.25); }

/* ❌ ผิด: สีเต็ม */
.badge { background: #00D27A; color: white; }  /* อย่าทำ */
```

---

## 6. Buttons

### Hierarchy
```css
/* Primary action (1 ต่อ section) */
.btn-wc-primary {
  background: var(--app-primary);
  color: #fff;
  border: none;
  border-radius: 0.375rem;   /* 6px */
  padding: .5rem 1.1rem;
  font-weight: 700;
  font-size: .85rem;
}

/* Secondary action */
.btn-wc-outline {
  background: transparent;
  border: 1.5px solid var(--app-primary);
  color: var(--app-primary);
  border-radius: 0.375rem;
  padding: .5rem 1.1rem;
  font-weight: 700;
  font-size: .85rem;
}

/* Destructive (ใช้น้อยมาก) */
.btn-danger-soft {
  background: rgba(230,55,87,.12);
  color: #c01236;
  border: none;
}
```

**กฎ:** ปุ่ม Primary action ≤ 1 ปุ่มต่อ section header

---

## 7. Page Structure (บังคับทุกหน้า /owner/)

```
{% extends "base.html" %}
{% load static %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/settings.css' %}">
{% endblock %}

{% block content %}

<!-- 1. Page Hero (บังคับ) -->
<div class="settings-hero">
  <div>
    <h1 class="settings-hero-title">
      <span class="hero-icon"><i class="bi bi-[icon]"></i></span>
      ชื่อหน้า
    </h1>
    <p class="settings-hero-sub">คำอธิบาย 1 บรรทัด</p>
  </div>
  <!-- Primary action button ถ้ามี -->
</div>

<!-- 2. Tabs ถ้ามีหลาย section (optional) -->

<!-- 3. Content ใน scard -->
<div class="scard">
  <div class="scard-header">...</div>
  <div class="scard-body">...</div>
</div>

{% endblock %}
```

---

## 8. Form Fields

```css
.form-label {
  font-size: .78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .06em;
  color: var(--bs-secondary-color);
  margin-bottom: .35rem;
}
.form-control {
  border-color: var(--bs-border-color);
  background: transparent;
  border-radius: .375rem;
  font-size: .88rem;
}
.form-control:focus {
  border-color: var(--app-primary);
  box-shadow: 0 0 0 3px rgba(201,169,110,.12);
}
```

---

## 9. Typography ใน Dashboard

| Element | Size | Weight | Transform |
|---------|------|--------|-----------|
| Page title | `1.45rem` | 800 | — |
| Section title | `0.97rem` | 700 | — |
| Table header | `0.72rem` | 700 | UPPERCASE |
| Form label | `0.78rem` | 700 | UPPERCASE |
| Body text | `0.88rem` | 400 | — |
| Muted/meta | `0.78rem` | 400 | — |
| Badge/chip | `0.72rem` | 700 | — |

---

## 10. สิ่งที่ห้ามทำ (Anti-patterns)

| ❌ ห้ามทำ | ✅ ทำแทน |
|----------|---------|
| Actions column ใน table | Clickable row |
| Border 1px บน card | Box-shadow |
| Hardcode hex color | CSS variable |
| Primary button > 1 ต่อ section | ใช้ outline สำหรับตัวอื่น |
| Status badge สีเต็ม | Soft color badge |
| สร้าง layout ใหม่ | ใช้ settings-hero + scard เสมอ |

---

## 11. ตัวอย่างหน้าที่ผ่าน Standard แล้ว

- `/owner/settings/` — settings.html (ต้นแบบ)
- `/owner/website-content/` — website_content.html

**อ้างอิงหน้าเหล่านี้เสมอก่อน implement หน้าใหม่**
