# CHECKLIST GO-LIVE CSC-MS | ITB Carnegie

## Infrastruktur (Web Editor)
- [ ] VPS Docker Compose (bukan hosting statis), disk/ram dan backup dipastikan tersedia.
- [ ] Subdomain `portal.itbcarnegie.com` DNS A/AAAA mengarah ke server yang benar.
- [ ] HTTPS/TLS aktif dan redirect HTTP→HTTPS; browser tidak memperingatkan sertifikat.
- [ ] `.env` dipasang di lokasi privat; `CSC_ENV=production`, `CSC_COOKIE_SECURE=1`.
- [ ] `data/`, SQLite, file bukti dan Google JSON tidak bisa diunduh via URL publik.
- [ ] Akun `DrSteven` dibuat dengan password sementara acak, langsung diganti. Tidak ada admin `123456` di produksi.
- [ ] User WR I, WR II, WR III (jika digunakan), Operator, Reviewer, PMB, Finance dibuat dengan password satu kali.
- [ ] Login gagal 5x memicu lock sementara; logout menghapus sesi.
- [ ] Pengguna lintas unit tidak bisa membaca/mengubah data yang bukan kewenangannya, diuji di API (bukan hanya menu).

## WR I
- [ ] Event baru mempunyai nama, tanggal, PIC, tujuan akademik/karakter.
- [ ] Agenda kegiatan bulanan dan rencana Imlek / seminar tersedia.
- [ ] Operator membuat penugasan terkait event beserta tenggat dan hasil.
- [ ] Proposal, bukti dan laporan akhir tercatat.

## WR II
- [ ] Kampanye baru, target konten, dan PIC dapat diinput.
- [ ] Tugas konten/story/feed/expo ada brief, target, PIC, tenggat.
- [ ] Berkas video / foto / PDF dapat diunggah dan hanya dapat dibuka pengguna berwenang.
- [ ] QC sebelum bukti ditolak oleh server; setelah bukti, penilaian 5 indikator berhasil.
- [ ] Penilaian mingguan otomatis terbentuk sesudah reviewer menyimpan QC.

## Referral dan Beasiswa
- [ ] Referensi belum diverifikasi tidak dapat dibebaskan Sabtu.
- [ ] PMB memasukkan bukti pendaftaran, Finance verifikasi lunas/terpenuhi.
- [ ] Setelah kedua verifikasi, WR II menyetujui pembebasan Sabtu 12 bulan; tidak berlaku surut.
- [ ] Penggunaan referensi sama untuk Taiwan memerlukan izin Rektor.
- [ ] Taiwan jalur alternatif hanya disetujui jika tugas QC diterima dengan nilai ≥85.
- [ ] Evaluasi tahunan dihitung 60/25/15 dan keputusan final hanya Rektor.
- [ ] Masa berlaku beasiswa lama dan hak pada kontrak lama diperiksa sebelum keputusan baru.

## Data & Google
- [ ] Spreadsheet CSC-MS menggunakan akun ITB Carnegie, master tidak dibagikan ke publik.
- [ ] Service account diberi akses tepat ke Sheet dan folder bukti.
- [ ] Sinkronisasi satu data setiap modul diverifikasi tercatat di tab yang benar.
- [ ] Backup file bukti ke Drive diuji, diuji juga akses file privat.
- [ ] Backup SQLite dan berkas bukti dilakukan serta restore diuji.
- [ ] Semua data uji/demo dihapus sebelum menerima data mahasiswa sebenarnya.

## Uji Browser (Wajib dilakukan di VPS)
- [ ] Desktop Chrome/Edge, Android, dan Safari iPhone bila tersedia.
- [ ] Form Tambah/Edit tugas/event/kampanye, QC, login, reset password, logout, CSV.
- [ ] Form input tampil baik pada layar ponsel; modal scroll dan tabel dapat dibaca.
- [ ] Tidak ada error JavaScript di console maupun respons 500 di log.
- [ ] 1 minggu pilot dengan mahasiswa dan staf terpilih, dievaluasi WR I/WR II dan Rektor.
