// Data awal ini sengaja sederhana agar mudah diganti dengan API Flask atau script Python Anda.
const state = {
  settings: {
    siteName: "Masjid Jami Anyar",
    heroImage: "https://images.unsplash.com/photo-1584551246679-0daf3d275d0f?auto=format&fit=crop&w=1800&q=85"
  },
  prayers: [
    { name: "Subuh", time: "04:39" },
    { name: "Dzuhur", time: "11:56" },
    { name: "Ashar", time: "15:18" },
    { name: "Maghrib", time: "17:49" },
    { name: "Isya", time: "19:02" }
  ],
  imamSchedule: [
    ["Senin", "Ust. Hasan", "Ust. Yusuf", "Ust. Malik", "Ust. Ridwan", "Ust. Amar", "-"],
    ["Selasa", "Ust. Ridwan", "Ust. Amar", "Ust. Yusuf", "Ust. Hasan", "Ust. Malik", "-"],
    ["Rabu", "Ust. Malik", "Ust. Hasan", "Ust. Amar", "Ust. Yusuf", "Ust. Ridwan", "-"],
    ["Kamis", "Ust. Amar", "Ust. Malik", "Ust. Ridwan", "Ust. Hasan", "Ust. Yusuf", "-"],
    ["Jumat", "Ust. Yusuf", "Ust. Ridwan", "Ust. Hasan", "Ust. Malik", "Ust. Amar", "Khatib: KH. Ahmad"]
  ],
  contents: [
    { type: "artikel", title: "Adab Memakmurkan Masjid", date: "14 Juni 2026", excerpt: "Ringkasan kajian tentang keutamaan shalat berjamaah dan menjaga adab di rumah Allah." },
    { type: "berita", title: "Renovasi Tempat Wudhu Tahap Dua", date: "12 Juni 2026", excerpt: "Panitia pembangunan membuka laporan progres dan kebutuhan donasi lanjutan." },
    { type: "kegiatan", title: "Kajian Ahad Pagi", date: "16 Juni 2026", excerpt: "Kajian rutin keluarga muslim bersama Ustadz Muhammad Fauzan setelah shalat Subuh." }
  ],
  finances: [
    { date: "2026-06-01", desc: "Infaq Jumat", income: 6200000, expense: 0 },
    { date: "2026-06-04", desc: "Operasional kebersihan", income: 0, expense: 850000 },
    { date: "2026-06-08", desc: "Donasi renovasi", income: 3500000, expense: 0 },
    { date: "2026-06-10", desc: "Perbaikan sound system", income: 0, expense: 1250000 }
  ],
  dkm: [
    { role: "Ketua DKM", name: "H. Abdul Karim" },
    { role: "Sekretaris", name: "Ahmad Maulana" },
    { role: "Bendahara", name: "Siti Aminah" },
    { role: "Bidang Ibadah", name: "Ust. Hasan Basri" },
    { role: "Bidang Sosial", name: "Nadia Rahmah" },
    { role: "Bidang Remaja Masjid", name: "Fikri Hidayat" }
  ]
};

const rupiah = new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", maximumFractionDigits: 0 });

function qs(selector) {
  return document.querySelector(selector);
}

async function loadPublicData() {
  // Kerangka integrasi API:
  // 1. Endpoint Flask /api/public mengirim settings, konten, jadwal, keuangan, dan DKM.
  // 2. Endpoint /api/prayer-times dapat diganti agar memanggil script Python jadwal shalat dari GitHub Anda.
  try {
    const response = await fetch("/api/public");
    if (!response.ok) return state;
    const data = await response.json();
    return { ...state, ...data };
  } catch {
    return state;
  }
}

function getNextPrayer(prayers) {
  const now = new Date();
  const minutesNow = now.getHours() * 60 + now.getMinutes();
  return prayers.find((item) => {
    const [hour, minute] = item.time.split(":").map(Number);
    return hour * 60 + minute >= minutesNow;
  })?.name || prayers[0].name;
}

function renderPrayerTimes(data) {
  const nextPrayer = getNextPrayer(data.prayers);
  qs("[data-prayer-grid]").innerHTML = data.prayers.map((item) => `
    <article class="prayer-card ${item.name === nextPrayer ? "is-next" : ""}">
      <span>${item.name}</span>
      <strong>${item.time}</strong>
      <small>${item.name === nextPrayer ? "Berikutnya" : "WIB"}</small>
    </article>
  `).join("");
}

function renderHijriDate() {
  // Placeholder kalender Hijriyah. Nanti bisa diganti dengan hasil script Python atau API kalender.
  const date = new Intl.DateTimeFormat("id-ID-u-ca-islamic", {
    weekday: "long", day: "numeric", month: "long", year: "numeric"
  }).format(new Date());
  qs("[data-hijri-date]").textContent = date;
}

function renderImamSchedule(data) {
  qs("[data-imam-table]").innerHTML = data.imamSchedule.map((row) => `
    <tr>${row.map((cell) => `<td>${cell}</td>`).join("")}</tr>
  `).join("");
}

function renderContents(data, filter = "semua") {
  const items = filter === "semua" ? data.contents : data.contents.filter((item) => item.type === filter);
  qs("[data-content-grid]").innerHTML = items.map((item) => `
    <article class="content-card">
      <div class="content-card__image" aria-hidden="true"></div>
      <div class="content-card__body">
        <span class="content-card__meta">${item.type} • ${item.date}</span>
        <h3>${item.title}</h3>
        <p>${item.excerpt}</p>
      </div>
    </article>
  `).join("");
}

function renderFinance(data) {
  const income = data.finances.reduce((sum, item) => sum + Number(item.income), 0);
  const expense = data.finances.reduce((sum, item) => sum + Number(item.expense), 0);
  const balance = income - expense;
  const max = Math.max(income, expense, Math.abs(balance), 1);

  qs("[data-finance-summary]").innerHTML = `
    <article class="summary-card"><span>Total Pemasukan</span><strong>${rupiah.format(income)}</strong></article>
    <article class="summary-card"><span>Total Pengeluaran</span><strong>${rupiah.format(expense)}</strong></article>
    <article class="summary-card"><span>Saldo Kas</span><strong>${rupiah.format(balance)}</strong></article>
  `;
  qs("[data-finance-chart]").innerHTML = `
    <div class="chart__bar">
      <strong>${rupiah.format(income)}</strong>
      <div class="chart__fill chart__fill--income" style="height:${(income / max) * 100}%"></div>
      <span>Pemasukan</span>
    </div>
    <div class="chart__bar">
      <strong>${rupiah.format(expense)}</strong>
      <div class="chart__fill chart__fill--expense" style="height:${(expense / max) * 100}%"></div>
      <span>Pengeluaran</span>
    </div>
    <div class="chart__bar">
      <strong>${rupiah.format(balance)}</strong>
      <div class="chart__fill chart__fill--balance" style="height:${(Math.abs(balance) / max) * 100}%"></div>
      <span>Saldo Kas</span>
    </div>
  `;
  qs("[data-finance-table]").innerHTML = data.finances.map((item) => `
    <tr>
      <td>${item.date}</td>
      <td>${item.desc}</td>
      <td>${rupiah.format(item.income)}</td>
      <td>${rupiah.format(item.expense)}</td>
    </tr>
  `).join("");
}

function renderDkm(data) {
  qs("[data-dkm-grid]").innerHTML = data.dkm.map((item) => `
    <article class="dkm-card">
      <strong>${item.role}</strong>
      <span>${item.name}</span>
    </article>
  `).join("");
}

function bindNavigation() {
  const header = qs("[data-header]");
  const nav = qs("[data-nav]");
  const toggle = qs("[data-nav-toggle]");
  const links = document.querySelectorAll("[data-nav-link]");

  toggle.addEventListener("click", () => {
    const isOpen = nav.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", String(isOpen));
  });

  nav.addEventListener("click", (event) => {
    if (event.target.closest("a")) {
      nav.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
    }
  });

  window.addEventListener("scroll", () => header.classList.toggle("is-scrolled", window.scrollY > 20), { passive: true });

  const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      links.forEach((link) => {
        link.classList.toggle("is-active", link.getAttribute("href") === `#${entry.target.id}`);
      });
    });
  }, { rootMargin: "-35% 0px -55% 0px", threshold: 0 });

  links.forEach((link) => {
    const section = qs(link.getAttribute("href"));
    if (section) sectionObserver.observe(section);
  });
}

function bindThemeToggle() {
  const button = qs("[data-theme-toggle]");
  const icon = qs("[data-theme-icon]");
  if (!button || !icon) return;

  const applyTheme = (theme) => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("theme", theme);
    const isDark = theme === "dark";
    icon.textContent = isDark ? "☀" : "☾";
    button.setAttribute("aria-label", isDark ? "Ganti ke mode terang" : "Ganti ke mode gelap");
  };

  applyTheme(localStorage.getItem("theme") || document.documentElement.dataset.theme || "light");
  button.addEventListener("click", () => {
    const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    applyTheme(nextTheme);
  });
}

function bindFilters(data) {
  document.querySelectorAll("[data-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll("[data-filter]").forEach((item) => item.classList.remove("is-active"));
      button.classList.add("is-active");
      renderContents(data, button.dataset.filter);
    });
  });
}

function applySettings(data) {
  qs("[data-site-name]").textContent = data.settings.siteName;
  qs("[data-hero-title]").textContent = data.settings.siteName;
  qs("[data-hero]").style.backgroundImage = `url("${data.settings.heroImage}")`;
}

document.addEventListener("DOMContentLoaded", async () => {
  const data = await loadPublicData();
  bindNavigation();
  bindThemeToggle();
  applySettings(data);
  renderHijriDate();
  renderPrayerTimes(data);
  renderImamSchedule(data);
  renderContents(data);
  renderFinance(data);
  renderDkm(data);
  bindFilters(data);
});
