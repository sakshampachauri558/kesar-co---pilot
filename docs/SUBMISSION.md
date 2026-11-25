# Submission Guide

Submit within **4 days** of receiving the assignment (the exact deadline is in your invitation email). Late submissions are only accepted if you let us know in advance.

---

## What to submit

Create a **GitHub repository** (public, or private with access granted to the reviewer account in your invitation email) with this structure:

```
your-submission/
├── README.md                 ← based on templates/SUBMISSION_README_TEMPLATE.md
├── TEST_REPORT.md            ← based on templates/test_report_template.md
├── workflow/
│   └── *.json                ← exported workflow(s) / scenario blueprint(s). NO secrets
├── prompts/                  ← (optional) prompts as .md/.txt files
├── code/                     ← (optional) any code nodes or scripts
└── screenshots/
    ├── workflow.png          ← full workflow canvas
    ├── tickets.png           ← the Tickets tab with the tickets created
    └── audit_log.png         ← the Audit Log tab with all 25 rows
```

## Checklist

- [ ] **Workflow export** (n8n JSON / Make blueprint / Zapier export) in `workflow/`
- [ ] **No API keys or tokens** anywhere in the repo (search your export for `key`, `token`, `secret`, `Bearer`, `sk-`)
- [ ] **Google Sheet link** (view access) in your README, showing all 25 emails processed and the tickets created
- [ ] **Screenshots** of the Tickets tab, audit log and workflow
- [ ] **TEST_REPORT.md** with v2 results for all 25 emails, your v1 comparison (at least 10 emails), and the failures you couldn't fix
- [ ] **README.md** with setup steps, architecture, decisions, scaling notes and the **5 product-thinking answers**
- [ ] **5-minute screen recording** (Loom, Google Drive or YouTube unlisted), linked in your README. Show:
  - your workflow and a quick tour of its main branches
  - at least **three emails running end-to-end**, including one that creates a ticket
  - one thing that **doesn't** work well yet, and why
- [ ] A short note in your README on **how you used AI tools**

## How to send it

Reply to your invitation email with:

1. The link to your GitHub repository
2. The link to your recording
3. The link to your Google Sheet

## After you submit

We review every submission against the requirements in the main [README](../README.md). Shortlisted candidates are invited to a **live session (about 60 minutes)** to walk us through the build and make a small change to it live. Please keep your workflow and Google Sheet running until you hear back from us.
