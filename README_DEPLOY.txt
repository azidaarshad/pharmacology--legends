PHARMACOLOGY LEGENDS V3 — LARGE JSU MOBA BANK

132 gameplay items:
• 80 MCQ (20 official-JSU subset + 60 training/battle)
• 20 SEQ (4 official-JSU subset + 16 training/battle)
• 20 Crisis missions
• 2 DOPS official JSU
• 10 Final Boss

Official JSU assessment remains 20 SER, 2 DOPS, 20 MCQ, 4 SEQ with 20/20/20/40% weightage.
The extra game items are for training/battle and do not change the official assessment structure.

Deployment:
1. Preserve the existing D1 database_id/binding DB. Replace the placeholder in wrangler.jsonc with your existing ID.
2. Deploy worker.js and public/index.html.
3. Confirm D1 binding name is DB and Connected.
4. GM URL: /?gm=1
5. Trainee URL: normal URL.
6. Flow: 80 MCQ → 20 SEQ → 20 Crisis → 2 DOPS → 10 Final Boss.
7. SEQ is no longer self-graded: trainee submits text; GM marks 0–100 via the backend.
8. DOPS/Crisis/Boss are lecturer-scored.
9. CSV reports are included.
