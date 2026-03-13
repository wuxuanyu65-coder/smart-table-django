// Lightweight active state for category chips
document.addEventListener("click", function (e) {
  const btn = e.target.closest(".menu-categories .category");
  if (btn) {
    const wrap = btn.closest(".menu-categories");
    wrap.querySelectorAll(".category").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
  }
});
