# CSC-MS WEB — ITB Carnegie 2027/2028
## Carnegie Scholarship & Activity Portal | Source code aplikasi operasional

**Pemilik proyek:** ITB Carnegie, Medan. **Sasaran domain:** `portal.itbcarnegie.com` (perlu dihubungkan oleh web editor). **Status:** source code aplikasi lengkap untuk dijalankan pada hosting Python/Docker; **belum diunggah ke server domain dan belum terhubung dengan kredensial Google API**.

Paket ini **bukan lagi prototipe HTML yang menyimpan data pada browser**. Tersedia backend FastAPI, API yang memeriksa hak akses, database SQLite permanen, modul tugas/event/marketing/QC, file bukti privat, pengguna dan password, audit, serta konfigurasi optional sinkronisasi Google Sheets/Drive. Tampilan memakai styling dashboard WR I/WR II yang sudah disetujui Rektor.

### 1. Fitur yang dapat digunakan setelah server dijalankan

- Login dengan akun individu dan password sementara yang **wajib diganti pada login pertama**. Akun Rektor dapat dibuat dengan username `DrSteven`.
- Rektor/Admin: dashboard gabungan, data semua unit, membuat akun staf, reset password, keputusan akhir evaluasi beasiswa dan Taiwan, audit dan integrasi.
- WR I: seminar, event mahasiswa (Imlek, YAWP, Summer Camp, Di Zi Gui, leadership, showcase), rencana/target/penugasan, data akademik, penilaian tahunan.
- WR II: kalender kampanye, konten/Reels/feed/story, expo, presentasi, penugasan marketing, mahasiswa pemberi referensi, pembebasan Sabtu.
- WR III: role tersedia untuk tugas/unit khusus bila diaktifkan Rektor (belum ada SOP kerja WR III spesifik).
- Operator/PIC reviewer: mencatat penugasan/absensi, mengunggah bukti, QC dengan lima indikator penilaian. Akun operator wajib diberi unit; server hanya mengizinkan unitnya.
- PMB/Finance: memvalidasi referensi dan pembayaran secara terpisah. Pembebasan Sabtu tidak bisa disetujui sebelum keduanya memverifikasi.
- Beasiswa: 100%, 70%, 50%, kuota penerimaan baru 2/3/50, setahun, evaluasi 60% kontribusi + 25% akademik + 15% karakter, keputusan akhir Rektor. Hak kontrak lama tetap harus dihormati.
- Taiwan: exchange Shih Hsin, Shih Chien, NCUE; 3+2 MCUT. Kontribusi 1 referensi terverifikasi ATAU proyek yang telah diterima QC minimal 85. Persyaratan akademik/mitra wajib diperiksa dan tidak ada jaminan diterima.
- Dokumen SOP yang sudah disahkan dapat diunduh dari portal setelah login.
- Pencatatan berbasis database server, bukan data simulasi / localStorage. File video, foto, PDF, Word dan Excel dapat diunggah sebagai bukti (default maksimal 50 MB per file).

### 2. Penginstalan server (direkomendasikan Docker)

**Perlu:** VPS Linux dengan Docker Engine + Docker Compose v2, domain/subdomain yang dapat diatur DNS-nya, dan port 80/443. **Hosting yang hanya melayani HTML/PHP statis tidak cukup** untuk backend Python ini. Jika `itbcarnegie.com` berada di shared hosting, web editor bisa menggunakan VPS untuk subdomain tanpa memindahkan website utama.

1. Ekstrak ZIP dan unggah seluruh folder proyek ke server. Jangan letakkan `.env`, `data/`, dan `secrets/` di dalam public web root.
2. Arahkan DNS record **A/AAAA** untuk `portal.itbcarnegie.com` ke IP publik VPS.
3. Di folder proyek server, jalankan `cp .env.example .env`, lalu sesuaikan `CSC_DOMAIN=portal.itbcarnegie.com`. Pastikan `CSC_ENV=production`, `CSC_COOKIE_SECURE=1`.
4. Jalankan `docker compose up -d --build`. Reverse proxy Caddy akan melayani HTTPS otomatis apabila DNS dan port terbuka.
5. Buat akun pertama secara **privat di terminal server**: `docker compose exec app python manage.py bootstrap-admin --username DrSteven`. Sistem akan membuat password sementara kuat secara otomatis dan menampilkannya **sekali**. Catat melalui media aman, kemudian login dan **langsung ganti password**.
6. Setelah login Rektor, buka **Manajemen Akun** untuk membuat WR I, WR II, WR III, operator, PIC/reviewer, PMB, dan Finance. Password acak baru tampil sekali. Setiap pengguna harus mengganti password pada login pertama.
7. Buka portal dengan HTTPS dan lakukan verifikasi fungsi menggunakan daftar pada `docs/CHECKLIST_GO_LIVE.md` sebelum input data asli.

> **Mengenai password `123456`:** karena angka tersebut sudah diketahui publik dan sangat mudah ditebak, **tidak boleh menjadi password admin untuk portal yang diakses lewat Internet**. Ada opsi lokal khusus jika ingin mencoba: pada komputer **offline/localhost** saja, set `CSC_ENV=development`, `CSC_BOOTSTRAP_PASSWORD=123456`, lalu jalankan `python manage.py bootstrap-admin --allow-weak-local`. Login pertama wajib mengganti password. Aplikasi memiliki pengaman agar admin dengan password sementara `123456` tidak dapat menjalankan server dalam mode `production`. **Untuk website sungguhan gunakan password sementara acak bawaan.**

### 3. Jalankan lokal (untuk pengetesan web editor)

Perlu Python **3.12+**.

```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
export CSC_ENV=development  # Windows PowerShell: $env:CSC_ENV='development'
export CSC_COOKIE_SECURE=0
python manage.py bootstrap-admin --username DrSteven
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Buka `http://127.0.0.1:8000`. **Jangan** menggunakan mode development untuk domain publik. Data lokal disimpan di folder `data/` yang otomatis dibuat.

### 4. Google Drive dan Google Sheets

Akun Google Drive yang digunakan untuk struktur awal adalah **ITB Carnegie (`itbcarnegie@gmail.com`)**, bukan akun Carnegie School.

- Google Drive: https://drive.google.com/drive/folders/12a2u3C7yRWFweeEuO6kZB2Eaat34C292
- Google Sheets: https://docs.google.com/spreadsheets/d/152y6XSRb3xN3q0sSSJurTmL7HMM17d2DB1wvnGZcJhk/edit

Sudah disediakan 19 tab Google Sheets, termasuk `WEEKLY_SCORES`, `REFERRALS_RESTRICTED`, `AUDIT_LOG`, dan `TAIWAN_APPLICATIONS`.

**Desain data:** SQLite adalah database utama yang menjamin login, transaksi, konsistensi, dan audit; Google Sheets adalah salinan data kerja (mirror), Google Drive untuk backup file bukti. Google Drive *sendiri* bukan database relasional. Ini kompromi teknis agar portal tetap bekerja saat Google API bermasalah.

Untuk menghubungkan Google:

1. Web editor membuat project Google Cloud dan mengaktifkan **Google Sheets API** dan **Google Drive API**.
2. Buat service account untuk aplikasi; unduh JSON kredensial **ke server privat saja** (bukan ke publik, bukan ke ZIP). Berikan izin editor pada spreadsheet serta folder Google Drive kepada email service account.
3. Di server, buat `secrets/google-service-account.json`; pemilik file sebaiknya UID 10001, permission `0400`. Aktifkan baris volume mount pada `docker-compose.yml` dan restart layanan.
4. Variabel `.env`: `GOOGLE_SERVICE_ACCOUNT_JSON_PATH=/run/secrets/google-service-account.json`, `GOOGLE_SHEET_ID=152y6XSRb3xN3q0sSSJurTmL7HMM17d2DB1wvnGZcJhk`, `GOOGLE_DRIVE_FOLDER_ID=12a2u3C7yRWFweeEuO6kZB2Eaat34C292`.
5. Menu **Google & Pengaturan** → **Sinkronkan 40 Record**. Setelah service account dan izin siap, sistem juga melakukan sinkronisasi antrean secara berkala (default setiap 90 detik).
6. Menu **Backup Bukti ke Drive** mengirim salinan file yang belum tersalin. File bukti tetap disimpan di volume server. Pantau antrean dan kegagalan; jangan menghapus file lokal hanya karena mirror Google sudah ada.

**Tidak ada kunci Google API dalam ZIP ini.** Tidak seorang pun dapat melakukan sinkronisasi sebelum web editor mengotorisasi koneksinya.

### 5. Struktur penting ZIP

```text
backend/main.py             API, login, RBAC, workflow, QC, referrals, Taiwan
backend/database.py         SQLite, audit, antrean sinkronisasi
backend/security.py         Hash password Argon2, session, pembatasan role
backend/google_sync.py      Google Sheets mirror + backup Drive opsional
web/index.html              Halaman aplikasi
web/assets/styles.css       Layout dashboard yang disetujui
web/assets/portal.css       Tampilan login dan fitur produksi
web/assets/portal.js        JavaScript dashboard dan formulir (API real)
web/assets/favicon.svg      Identitas aplikasi
manage.py                   Setup admin dan backup database
Dockerfile                  Container aplikasi Python
Caddyfile                   Reverse proxy HTTPS
docker-compose.yml          Container aplikasi dan reverse proxy
.env.example                Contoh konfigurasi server tanpa password
requirements.txt            Dependensi backend
reference_layout/*.png      Gambar acuan desain WR I, WR II, Rektor, mobile, login
docs/                       SOP, instruksi web editor, checklist keamanan
scripts/                    Utilitas setup/backup

tests/test_portal.py        Uji alur backend otomatis
```

### 6. Backup, pemulihan, dan hak akses

- Jalankan rutin `docker compose exec app python manage.py backup` untuk backup SQLite konsisten. Lokasi backup berada di volume privat aplikasi; **salin ke penyimpanan terpisah** dengan retensi yang sesuai.
- Pastikan hanya admin memiliki akses langsung ke database, akun Google service account, dan folder data sensitif.
- Pengguna mengakses data melalui portal, bukan dengan membagikan spreadsheet master ke seluruh staf.
- Jangan menyimpan password dalam Google Sheets atau file konfigurasi frontend.
- Rencanakan backup file `data/uploads/`, uji restore, dan rotasi backup sebelum mulai digunakan semua angkatan.

### 7. Pengujian yang sudah dilakukan untuk paket ini

- 6 suite pengujian otomatis backend berhasil: login & wajib ganti password; pembatasan peran; CSRF; QC dan upload bukti; referral PMB & Finance; pembebasan Sabtu; evaluasi Rektor; Taiwan referensi ganda dan alternatif QC ≥85.
- `node --check` berhasil memeriksa sintaks JavaScript.
- Endpoint `/health` berhasil diuji pada server Python lokal.
- **Belum diuji di VPS produksi**, termasuk Docker pada server pengguna, DNS, HTTPS domain, serta Google API dengan service account sungguhan. Lingkungan browser otomatis yang tersedia dalam sesi ini memblokir navigasi browser, sehingga pemeriksaan interaksi layar end-to-end di browser produksi **masih perlu dilakukan oleh web editor** menggunakan checklist go-live.

### 8. Batasan dan pengembangan lanjutan

- Tidak ada pembayaran online atau integrasi dengan rekening kampus; Finance hanya memverifikasi status secara administratif. 
- Tidak tersedia akun mahasiswa untuk login sendiri pada versi awal; bukti diunggah oleh staf/PIC sesuai scope, atau dikirim mahasiswa kepada staf.
- Tidak ada jaminan e-signature bersertifikat, kelulusan universitas Taiwan, atau validitas hukum perjanjian; SOP/SK dan kewenangan ditetapkan institusi.
- Google Sheets adalah mirror operasional awal, bukan database utama. Untuk skala sangat besar, dapat dipindah ke PostgreSQL dan object storage tanpa mengubah struktur UI besar.
- Program WR III tersedia sebagai role dan scope tugas; sebelum menambah pekerjaan WR III, tetapkan SOP spesifiknya.

**Kesimpulan:** kode siap diserahkan ke web editor untuk dipasang pada VPS. Source berfungsi dengan database lokal sungguhan setelah instalasi dan bootstrap admin. Status **online di `portal.itbcarnegie.com` baru tercapai setelah DNS, server, HTTPS, service account Google, dan uji go-live diselesaikan.**
