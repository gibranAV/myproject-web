# Website Masjid Jami Anyar

Starter project website masjid interaktif dengan halaman publik, API, CMS admin, dan SQLite.

## Struktur Folder

```text
project/
├── .gitignore
├── index.html
├── app.py
├── requirements.txt
├── assets/
│   ├── css/style.css
│   └── js/main.js
├── static/
│   ├── css/admin.css
│   └── uploads/
└── templates/
    └── admin/dashboard.html
```

## Menjalankan Proyek

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Buka `http://127.0.0.1:5000` untuk halaman jamaah dan `http://127.0.0.1:5000/admin` untuk panel admin.

## Troubleshooting

- **ModuleNotFoundError: No module named 'flask'**: pastikan Anda mengaktifkan virtual environment lalu memasang dependensi:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

- Jika pip di dalam `.venv` perlu diperbarui:

```bash
.venv\Scripts\python.exe -m pip install --upgrade pip
```

## Login Admin

Gunakan akun awal berikut:

```text
Username: admin@masjid.org
Password: admin123
```

Untuk produksi, ganti username, password, dan `SECRET_KEY` di `app.py`.

## Integrasi Jadwal Shalat

Bagian jadwal shalat disiapkan di dua tempat:

- `assets/js/main.js` pada fungsi `loadPublicData()`
- `app.py` pada fungsi `prayer_times_placeholder()`

Ganti isi `prayer_times_placeholder()` agar memanggil script Python dari repositori GitHub Anda, lalu kirim hasilnya dengan format:

```json
[
  { "name": "Subuh", "time": "04:39" },
  { "name": "Dzuhur", "time": "11:56" }
]
```

## Catatan Pengembangan

- Frontend memakai HTML, CSS, dan JavaScript vanilla.
- Backend memakai Flask dan SQLite agar ringan untuk hosting sederhana.
- Panel admin ini kerangka CMS awal. Untuk produksi, tambahkan login admin, validasi role, CSRF protection, dan backup database berkala.
