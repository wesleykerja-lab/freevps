# Laporan Pemeriksaan Paket CSC-MS WEB

- Python backend syntax: PASS (`py_compile`).
- JavaScript syntax: PASS (`node --check`).
- API server startup & GET `/health`: PASS pada pengujian lokal.
- 6 suite unit/integration tests via FastAPI TestClient: PASS.
- Login, forced change, password policy, CSRF, logout/session invalidation: PASS.
- Scope WR I/WR II: PASS.
- Upload bukti + larangan QC tanpa bukti + QC score: PASS.
- Referral dua pihak + Saturday exemption 12 bulan + larangan duplikat: PASS.
- Evaluasi tahunan: PASS.
- Program Taiwan referral reuse dan proyek alternatif QC ≥85: PASS.
- Google Sheets live sync: NOT TESTED (service-account credentials not installed).
- HTTPS & domain portal.itbcarnegie.com: NOT DEPLOYED/NOT TESTED (web editor needs domain/server access).
- Docker build on target VPS: NOT TESTED (Docker CLI unavailable in build environment).
- Browser navigation automation: BLOCKED BY TEST ENVIRONMENT POLICY (Playwright could not navigate even to local/data pages); test UI in production checklist.

Ini menjelaskan dengan tepat apa yang sudah dan belum terverifikasi. Semua hasil di atas berdasarkan kode pada paket ini; file `data/` test privat dan akun tes tidak disertakan dalam ZIP.
