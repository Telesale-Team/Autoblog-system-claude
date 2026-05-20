(function () {
  const blocks = document.querySelectorAll(".yw-article-body pre, .article-body pre");
  if (!blocks.length) return;

  blocks.forEach((pre) => {
    if (pre.querySelector(".code-copy-btn")) return;

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "code-copy-btn";
    btn.setAttribute("aria-label", "คัดลอกโค้ด");
    btn.innerHTML = '<span class="copy-icon">📋</span><span class="copy-label">Copy</span>';

    btn.addEventListener("click", async () => {
      const code = pre.querySelector("code");
      const text = (code ? code.innerText : pre.innerText).replace(/\n$/, "");
      try {
        await navigator.clipboard.writeText(text);
        btn.classList.add("copied");
        btn.querySelector(".copy-label").textContent = "Copied!";
        btn.querySelector(".copy-icon").textContent = "✓";
        setTimeout(() => {
          btn.classList.remove("copied");
          btn.querySelector(".copy-label").textContent = "Copy";
          btn.querySelector(".copy-icon").textContent = "📋";
        }, 1800);
      } catch (e) {
        btn.querySelector(".copy-label").textContent = "Failed";
        setTimeout(() => {
          btn.querySelector(".copy-label").textContent = "Copy";
        }, 1800);
      }
    });

    pre.appendChild(btn);
  });
})();
