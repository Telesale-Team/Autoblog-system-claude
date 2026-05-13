(function () {
  const body = document.querySelector(".article-body");
  const tocNav = document.getElementById("article-toc");
  if (!body || !tocNav) return;

  const headings = body.querySelectorAll("h2, h3");
  if (!headings.length) {
    tocNav.innerHTML = '<p class="text-secondary small mb-0 px-3 py-2">บทความนี้ยังไม่มีหัวข้อย่อย</p>';
    return;
  }

  const slugify = (text, idx) => {
    const s = text
      .toString()
      .trim()
      .toLowerCase()
      .replace(/[^\p{L}\p{N}]+/gu, "-")
      .replace(/^-+|-+$/g, "");
    return s ? `h-${s.slice(0, 60)}-${idx}` : `h-${idx}`;
  };

  const ul = document.createElement("ul");
  const items = [];
  headings.forEach((h, i) => {
    if (!h.id) h.id = slugify(h.textContent, i);
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.href = `#${h.id}`;
    a.textContent = h.textContent;
    a.className = h.tagName === "H3" ? "toc-h3" : "toc-h2";
    a.addEventListener("click", (e) => {
      e.preventDefault();
      const target = document.getElementById(h.id);
      if (target) {
        const top = target.getBoundingClientRect().top + window.pageYOffset - 80;
        window.scrollTo({ top, behavior: "smooth" });
        history.replaceState(null, "", `#${h.id}`);
      }
    });
    li.appendChild(a);
    ul.appendChild(li);
    items.push({ id: h.id, link: a, el: h });
  });

  tocNav.innerHTML = "";
  tocNav.appendChild(ul);

  // Scroll spy
  const setActive = () => {
    const scrollPos = window.scrollY + 120;
    let activeIdx = 0;
    for (let i = 0; i < items.length; i++) {
      if (items[i].el.offsetTop <= scrollPos) activeIdx = i;
    }
    items.forEach((it, i) => {
      const isActive = i === activeIdx;
      it.link.classList.toggle("active", isActive);
      if (isActive) {
        it.link.setAttribute("aria-current", "location");
      } else {
        it.link.removeAttribute("aria-current");
      }
    });
  };

  let ticking = false;
  window.addEventListener("scroll", () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        setActive();
        ticking = false;
      });
      ticking = true;
    }
  });
  setActive();

  // Mobile collapse — works on initial load AND resize
  const toggle = document.querySelector(".toc-toggle");
  if (toggle) {
    const mq = window.matchMedia("(max-width: 767.98px)");

    const applyMobileState = (isMobile) => {
      if (isMobile) {
        tocNav.classList.add("collapsed");
        toggle.textContent = "▶";
      } else {
        tocNav.classList.remove("collapsed");
        toggle.textContent = "▼";
      }
    };

    applyMobileState(mq.matches);
    mq.addEventListener("change", (e) => applyMobileState(e.matches));

    toggle.addEventListener("click", () => {
      const collapsed = tocNav.classList.toggle("collapsed");
      toggle.textContent = collapsed ? "▶" : "▼";
    });
  }
})();
