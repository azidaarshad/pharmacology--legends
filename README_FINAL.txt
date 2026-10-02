NSNT LEGENDS — FINAL BUILD
===========================

Target Worker: pharmacology--legends
Existing Production D1 binding: DB -> pharmacology-legends-db

GAME / ASSESSMENT
-----------------
Question bank: 200 total
- 105 MCQ
- 40 SEQ
- 55 CLINICAL

Active trainee mission set: 95
- 90 MCQ
- 5 SEQ
- 0 CLINICAL

Frozen questions remain in the GM Question Bank but are not served to trainees.
Trainee order is individualized and shuffled within each unit while preserving:
Unit 1 -> Unit 2 -> Unit 3.
MCQ phase runs first, followed by SEQ.

SCORING
-------
Individual maximum: /95
Continuous Assessment conversion: /20%
MCQ: 45 seconds
SEQ: 120 seconds

DEPLOYMENT NOTE
---------------
The Cloudflare production Worker already has a dashboard D1 binding:
DB -> pharmacology-legends-db.
The repository Wrangler file therefore targets that exact database name.
The account-specific D1 UUID must be the UUID of the existing pharmacology-legends-db.
Do NOT create a new D1 database and do NOT change the existing dashboard binding.

Before deployment, replace the database_id placeholder in wrangler.jsonc with the
UUID of the EXISTING pharmacology-legends-db. Cloudflare requires a valid D1
UUID for a Wrangler-declared D1 binding.

Other code/UI corrections in this build:
- Worker name aligned to pharmacology--legends.
- All trainee/report score displays corrected to /95.
- Help text corrected from 200 missions to 95 active missions.
- 200 remains the GM Question Bank total.


RUNTIME FIX VERIFIED: embedded trainee page now receives the real TOPICS object; the previous TOPICS_PLACE placeholder has been removed so Team A-F buttons initialize correctly. Trainee individual maximum is displayed as /95.
