# Pharmacology Legends — Online Classroom Game

## Versi ini sudah FINAL untuk rekod markah
- 6 team: A–F, maksimum 10 pelajar setiap team.
- Student masuk melalui link/QR.
- Semua pelajar menjawab mengikut urutan soalan/topik.
- HP / XP / coin dikongsi secara live.
- Ada timer, attack, unlock topic dan Final Boss.
- GM boleh download `CSV report` selepas kelas.
- **Game state + sejarah jawapan disimpan dalam SQLite**, jadi markah tidak hilang apabila server restart/redeploy **jika Render Persistent Disk dipasang pada `/var/data`**.

## Penting untuk Render
Render menggunakan filesystem ephemeral secara default. Persistent Disk diperlukan untuk mengekalkan fail SQLite merentasi restart/deploy. Persistent Disk hanya tersedia pada paid service. citeturn0search0

Fail `render.yaml` dalam pakej ini sudah menetapkan:
- `plan: starter`
- `numInstances: 1`
- disk `/var/data`
- 1 GB storage

SQLite sesuai untuk game kelas yang menggunakan satu instance; Render juga menyatakan disk + SQLite sesuai untuk low-traffic single-instance app. citeturn0search3

## Deploy
1. Extract ZIP ini.
2. Upload semua fail dalam folder ini ke satu GitHub repository.
3. Di Render: **New → Web Service** dan sambungkan repository.
4. Jika Render membaca `render.yaml` sebagai Blueprint, gunakan konfigurasi tersebut.
5. Jika setup manual, gunakan:
   - Build: `pip install -r requirements.txt`
   - Start: `python server.py`
   - Plan: paid plan yang menyokong Persistent Disk
   - Disk mount path: `/var/data`
   - Size: 1 GB
6. Selepas deploy, buka URL `onrender.com` yang diberikan Render.
7. Untuk pensyarah, buka `?gm=1` pada hujung URL.
8. QR pada skrin GM akan menjana link pelajar secara automatik.

Contoh:
- Student: `https://nama-game.onrender.com`
- GM: `https://nama-game.onrender.com?gm=1`

Render web service mendapat URL `onrender.com` dan perlu menerima trafik pada port yang ditetapkan oleh environment `PORT`; kod ini sudah bind ke `0.0.0.0`. citeturn0search4

## Selepas kelas
Pada skrin GM tekan **DOWNLOAD REPORT** untuk simpan CSV. Report mengandungi:
- soalan
- topik
- tahap kesukaran
- nama pelajar
- team
- betul/salah
- markah
- masa jawapan

## Nota penting
Jawapan dalam versi ini ialah **self-report Betul/Salah** selepas pelajar menjawab secara lisan/kelas. Pensyarah/GM masih menjadi pengesah jawapan. Ini sesuai untuk gamifikasi kelas, bukan peperiksaan berpengawasan automatik.
