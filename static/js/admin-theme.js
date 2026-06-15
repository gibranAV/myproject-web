(function () {
  // Menyimpan pilihan dark/light mode agar tetap sama saat halaman admin dibuka ulang.
  var savedTheme = localStorage.getItem("theme") || "light";
  var root = document.documentElement;

  function applyTheme(theme) {
    var isDark = theme === "dark";
    root.dataset.theme = theme;
    localStorage.setItem("theme", theme);
    document.querySelectorAll("[data-theme-toggle]").forEach(function (button) {
      button.setAttribute("aria-label", isDark ? "Ganti ke mode terang" : "Ganti ke mode gelap");
    });
    document.querySelectorAll("[data-theme-icon]").forEach(function (icon) {
      icon.textContent = isDark ? "☀" : "☾";
    });
  }

  applyTheme(savedTheme);
  document.querySelectorAll("[data-theme-toggle]").forEach(function (button) {
    button.addEventListener("click", function () {
      applyTheme(root.dataset.theme === "dark" ? "light" : "dark");
    });
  });
})();
