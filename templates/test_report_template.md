# Test Report — Kesar & Co. Support Copilot

**Candidate name:**
**Platform used:** n8n / Make / Zapier / other: ____
**LLM(s) used:** (provider + model name)

---

## 1. How I decided what "correct" means

Before measuring accuracy, write down your own expected outcome for each email (intent + action) **based on `data/faq.md` and `data/orders.json`**. Explain any judgment calls in 3–5 lines here.

## 2. Results per email

Fill one row per email. "Expected" is your own judgment. For "Action", describe what the flow did (e.g., *draft reply*, *ticket TKT-004*, *needs human*, *log only*).

v2 (your final version) must cover all 25 emails. v1 needs at least 10. Put `—` in the v1 columns for emails you didn't run in v1.

| Email | Expected intent | Expected action | v1 intent | v1 action | v1 ✅/❌ | v2 intent | v2 action | v2 ✅/❌ | Notes |
|---|---|---|---|---|---|---|---|---|---|
| E01 | | | | | | | | | |
| E02 | | | | | | | | | |
| E03 | | | | | | | | | |
| E04 | | | | | | | | | |
| E05 | | | | | | | | | |
| E06 | | | | | | | | | |
| E07 | | | | | | | | | |
| E08 | | | | | | | | | |
| E09 | | | | | | | | | |
| E10 | | | | | | | | | |
| E11 | | | | | | | | | |
| E12 | | | | | | | | | |
| E13 | | | | | | | | | |
| E14 | | | | | | | | | |
| E15 | | | | | | | | | |
| E16 | | | | | | | | | |
| E17 | | | | | | | | | |
| E18 | | | | | | | | | |
| E19 | | | | | | | | | |
| E20 | | | | | | | | | |
| E21 | | | | | | | | | |
| E22 | | | | | | | | | |
| E23 | | | | | | | | | |
| E24 | | | | | | | | | |
| E25 | | | | | | | | | |

## 3. Summary

*n* = the number of emails you ran in that version (at least 10 for v1, 25 for v2).

| Metric | Prompt v1 | Prompt v2 |
|---|---|---|
| Emails run (*n*) | | 25 |
| Intent accuracy (x / *n*) | | |
| Correct action (x / *n*) | | |
| Valid JSON on first try (x / *n*) | | |
| Emails sent to "needs human" | | |
| Avg. tokens per email (if tracked) | | |
| Est. cost per email (₹ or $) | | |

## 4. What I changed from v1 to v2, and why

- Change 1:
- Change 2:
- Change 3:

## 5. Failures I could not fix (be honest)

| Email | What goes wrong | Why I think it happens | What I would try next |
|---|---|---|---|
| | | | |
