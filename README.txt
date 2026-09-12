NSNT LEGENDS — FINAL COMPLETE BUILD

Cloudflare Worker/D1 build.

Files:
- worker.js — single Worker containing the 180-question bank and embedded frontend. This is the main deployment file.
- index.html — matching frontend copy for reference/local inspection.
- assets/ — 22 topic visual PNGs (1.1–1.6, 2.1–2.11.5, 3.0).
- wrangler.jsonc — D1 binding DB using the existing pharmacology-legends-db database ID.

Login:
- Full matric number only, e.g. DPNS1/2026(05)-0001.
- Trainee then chooses Team A–F.

Assessment/game:
- 180 missions: Nutrition 60 (30 MCQ, 15 SEQ, 15 Clinical) + Pharmacology 120 (55 MCQ, 25 SEQ, 40 Clinical).
- Individual: correct/earned normalized points only, no penalty; /180 -> CONT /20%.
- Team: correct +1, wrong -1.
- MCQ 45s; SEQ/Clinical 120s; automatic advance when timer expires.
- Randomized mission order per battle; MCQ options sorted shortest to longest while preserving the correct answer.
- Team leaderboard is public; other trainees' individual marks are hidden.
- GM sees full individual marks, submissions and report.
- Question Bank is GM-only; edits question/options/correct answer/reference answer/rubric.
- CSV and Excel report.
- Autosave in D1; controlled GM reset.
- Attack/HP/team battle and 10 Final Boss missions.
- DOPS and official Final assessment are not included in CONT game calculation.
- Original WebAudio MOBA-style music/SFX; no Mobile Legends audio.

Deployment:
Use worker.js as the Worker source. The Worker serves its embedded index.html, so no separate static-site deployment is required.
Keep the existing D1 binding name DB and existing database. Do not create a new D1 database.
