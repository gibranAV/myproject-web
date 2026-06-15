from pathlib import Path
import hmac
import sqlite3
from flask import Flask, jsonify, redirect, render_template, request, send_from_directory, session, url_for  # type: ignore[import]
from werkzeug.utils import secure_filename  # type: ignore[import]

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "mosque.db"
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
ADMIN_USERNAME = "admin@masjid.org"
ADMIN_PASSWORD = "admin123"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
# Kunci ini dipakai Flask untuk mengenkripsi session login.
# Untuk produksi, ganti dengan nilai panjang dan rahasia.
app.config["SECRET_KEY"] = "ganti-secret-key-masjid-jami-anyar"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_db():
    """Membuka koneksi SQLite dengan hasil baris berbentuk dictionary-like."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Membuat tabel dan data awal agar proyek langsung bisa dicoba."""
    with get_db() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS contents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                excerpt TEXT NOT NULL,
                body TEXT NOT NULL,
                published_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS finances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                income INTEGER DEFAULT 0,
                expense INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS dkm_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                name TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS imam_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT NOT NULL,
                subuh TEXT NOT NULL,
                dzuhur TEXT NOT NULL,
                ashar TEXT NOT NULL,
                maghrib TEXT NOT NULL,
                isya TEXT NOT NULL,
                special TEXT DEFAULT '-'
            );
            """
        )
        if not db.execute("SELECT value FROM settings WHERE key='site_name'").fetchone():
            db.executemany(
                "INSERT INTO settings (key, value) VALUES (?, ?)",
                [
                    ("site_name", "Masjid Jami Anyar"),
                    ("hero_image", "https://images.unsplash.com/photo-1584551246679-0daf3d275d0f?auto=format&fit=crop&w=1800&q=85"),
                ],
            )
            db.executemany(
                "INSERT INTO contents (type, title, excerpt, body, published_at) VALUES (?, ?, ?, ?, ?)",
                [
                    ("artikel", "Adab Memakmurkan Masjid", "Keutamaan shalat berjamaah dan menjaga adab di rumah Allah.", "Isi artikel dapat ditulis dari panel admin.", "2026-06-14"),
                    ("berita", "Renovasi Tempat Wudhu", "Laporan progres renovasi dan kebutuhan donasi.", "Isi berita dapat ditulis dari panel admin.", "2026-06-12"),
                    ("kegiatan", "Kajian Ahad Pagi", "Kajian rutin keluarga muslim setelah Subuh.", "Detail kegiatan dapat ditulis dari panel admin.", "2026-06-16"),
                ],
            )
            db.executemany(
                "INSERT INTO finances (date, description, income, expense) VALUES (?, ?, ?, ?)",
                [
                    ("2026-06-01", "Infaq Jumat", 6200000, 0),
                    ("2026-06-04", "Operasional kebersihan", 0, 850000),
                    ("2026-06-08", "Donasi renovasi", 3500000, 0),
                ],
            )
            db.executemany(
                "INSERT INTO dkm_members (role, name) VALUES (?, ?)",
                [("Ketua DKM", "H. Abdul Karim"), ("Sekretaris", "Ahmad Maulana"), ("Bendahara", "Siti Aminah")],
            )
            db.executemany(
                "INSERT INTO imam_schedules (day, subuh, dzuhur, ashar, maghrib, isya, special) VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    ("Senin", "Ust. Hasan", "Ust. Yusuf", "Ust. Malik", "Ust. Ridwan", "Ust. Amar", "-"),
                    ("Jumat", "Ust. Yusuf", "Ust. Ridwan", "Ust. Hasan", "Ust. Malik", "Ust. Amar", "Khatib: KH. Ahmad"),
                ],
            )


def setting(key, default=""):
    with get_db() as db:
        row = db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default


def set_setting(key, value):
    with get_db() as db:
        db.execute("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))


def prayer_times_placeholder():
    """Ganti isi fungsi ini dengan pemanggilan script Python jadwal shalat dari repositori GitHub Anda."""
    return [
        {"name": "Subuh", "time": "04:39"},
        {"name": "Dzuhur", "time": "11:56"},
        {"name": "Ashar", "time": "15:18"},
        {"name": "Maghrib", "time": "17:49"},
        {"name": "Isya", "time": "19:02"},
    ]


@app.before_request
def protect_admin_area():
    """Mengunci seluruh halaman dan aksi /admin kecuali halaman login."""
    if not request.path.startswith("/admin"):
        return None
    if request.endpoint == "admin_login":
        return None
    if session.get("admin_logged_in"):
        return None
    return redirect(url_for("admin_login", next=request.path))


@app.after_request
def disable_admin_cache(response):
    """Mencegah browser menampilkan ulang halaman admin setelah logout."""
    if request.path.startswith("/admin"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


@app.route("/")
def public_home():
    """Menyajikan halaman publik statis."""
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/assets/<path:filename>")
def public_assets(filename):
    """Menyajikan CSS dan JavaScript halaman publik."""
    return send_from_directory(BASE_DIR / "assets", filename)


@app.route("/api/public")
def api_public():
    """API untuk frontend umat. Bisa dipakai juga oleh mobile app di kemudian hari."""
    with get_db() as db:
        contents = [dict(row) for row in db.execute("SELECT * FROM contents ORDER BY published_at DESC LIMIT 6")]
        finances = [
            {"date": row["date"], "desc": row["description"], "income": row["income"], "expense": row["expense"]}
            for row in db.execute("SELECT * FROM finances ORDER BY date DESC LIMIT 8")
        ]
        dkm = [dict(row) for row in db.execute("SELECT role, name FROM dkm_members ORDER BY id")]
        imam = [
            [row["day"], row["subuh"], row["dzuhur"], row["ashar"], row["maghrib"], row["isya"], row["special"]]
            for row in db.execute("SELECT * FROM imam_schedules ORDER BY id")
        ]
    return jsonify(
        {
            "settings": {"siteName": setting("site_name"), "heroImage": setting("hero_image")},
            "prayers": prayer_times_placeholder(),
            "contents": [
                {"type": row["type"], "title": row["title"], "date": row["published_at"], "excerpt": row["excerpt"]}
                for row in contents
            ],
            "finances": finances,
            "dkm": dkm,
            "imamSchedule": imam,
        }
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Login admin sederhana dengan username dan password yang sudah ditentukan."""
    error = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        valid_username = hmac.compare_digest(username, ADMIN_USERNAME)
        valid_password = hmac.compare_digest(password, ADMIN_PASSWORD)
        if valid_username and valid_password:
            session.clear()
            session["admin_logged_in"] = True
            session["admin_username"] = ADMIN_USERNAME
            next_url = request.args.get("next")
            if next_url and next_url.startswith("/admin"):
                return redirect(next_url)
            return redirect(url_for("admin_dashboard"))
        error = "Username atau password salah."
    return render_template("admin/login.html", error=error)


@app.post("/admin/logout")
def admin_logout():
    """Menghapus session admin lalu kembali ke halaman login."""
    session.clear()
    return redirect(url_for("admin_login"))


@app.route("/admin")
def admin_dashboard():
    with get_db() as db:
        data = {
            "site_name": setting("site_name"),
            "hero_image": setting("hero_image"),
            "contents": db.execute("SELECT * FROM contents ORDER BY published_at DESC").fetchall(),
            "finances": db.execute("SELECT * FROM finances ORDER BY date DESC").fetchall(),
            "dkm": db.execute("SELECT * FROM dkm_members ORDER BY id").fetchall(),
            "imam": db.execute("SELECT * FROM imam_schedules ORDER BY id").fetchall(),
        }
    return render_template("admin/dashboard.html", **data)


@app.post("/admin/settings")
def update_settings():
    set_setting("site_name", request.form["site_name"])
    file = request.files.get("hero_image")
    if file and file.filename:
        filename = secure_filename(file.filename)
        file.save(app.config["UPLOAD_FOLDER"] / filename)
        set_setting("hero_image", url_for("static", filename=f"uploads/{filename}"))
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/content")
def create_content():
    with get_db() as db:
        db.execute(
            "INSERT INTO contents (type, title, excerpt, body, published_at) VALUES (?, ?, ?, ?, ?)",
            (request.form["type"], request.form["title"], request.form["excerpt"], request.form["body"], request.form["published_at"]),
        )
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/content/<int:item_id>/update")
def update_content(item_id):
    with get_db() as db:
        db.execute(
            """
            UPDATE contents
            SET type=?, title=?, excerpt=?, body=?, published_at=?
            WHERE id=?
            """,
            (request.form["type"], request.form["title"], request.form["excerpt"], request.form["body"], request.form["published_at"], item_id),
        )
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/content/<int:item_id>/delete")
def delete_content(item_id):
    with get_db() as db:
        db.execute("DELETE FROM contents WHERE id=?", (item_id,))
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/finance")
def create_finance():
    with get_db() as db:
        db.execute(
            "INSERT INTO finances (date, description, income, expense) VALUES (?, ?, ?, ?)",
            (request.form["date"], request.form["description"], int(request.form.get("income") or 0), int(request.form.get("expense") or 0)),
        )
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/finance/<int:item_id>/update")
def update_finance(item_id):
    with get_db() as db:
        db.execute(
            """
            UPDATE finances
            SET date=?, description=?, income=?, expense=?
            WHERE id=?
            """,
            (request.form["date"], request.form["description"], int(request.form.get("income") or 0), int(request.form.get("expense") or 0), item_id),
        )
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/finance/<int:item_id>/delete")
def delete_finance(item_id):
    with get_db() as db:
        db.execute("DELETE FROM finances WHERE id=?", (item_id,))
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/dkm")
def create_dkm():
    with get_db() as db:
        db.execute("INSERT INTO dkm_members (role, name) VALUES (?, ?)", (request.form["role"], request.form["name"]))
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/dkm/<int:item_id>/update")
def update_dkm(item_id):
    with get_db() as db:
        db.execute("UPDATE dkm_members SET role=?, name=? WHERE id=?", (request.form["role"], request.form["name"], item_id))
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/dkm/<int:item_id>/delete")
def delete_dkm(item_id):
    with get_db() as db:
        db.execute("DELETE FROM dkm_members WHERE id=?", (item_id,))
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/imam")
def create_imam():
    with get_db() as db:
        db.execute(
            "INSERT INTO imam_schedules (day, subuh, dzuhur, ashar, maghrib, isya, special) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (request.form["day"], request.form["subuh"], request.form["dzuhur"], request.form["ashar"], request.form["maghrib"], request.form["isya"], request.form.get("special", "-")),
        )
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/imam/<int:item_id>/update")
def update_imam(item_id):
    with get_db() as db:
        db.execute(
            """
            UPDATE imam_schedules
            SET day=?, subuh=?, dzuhur=?, ashar=?, maghrib=?, isya=?, special=?
            WHERE id=?
            """,
            (request.form["day"], request.form["subuh"], request.form["dzuhur"], request.form["ashar"], request.form["maghrib"], request.form["isya"], request.form.get("special", "-"), item_id),
        )
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/imam/<int:item_id>/delete")
def delete_imam(item_id):
    with get_db() as db:
        db.execute("DELETE FROM imam_schedules WHERE id=?", (item_id,))
    return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
