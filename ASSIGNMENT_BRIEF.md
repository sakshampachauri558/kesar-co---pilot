# AI Automation Intern — Take-home Assignment
## Build an AI Order-Support Copilot for "Kesar & Co."

Thanks for your interest in the **AI Automation Intern** role. This assignment is a small, realistic version of the work you'd do with us: designing an automation that uses an LLM, connects real tools, behaves safely, and is documented well enough that someone else could run it.

We care about **how you think** as much as what you build. A smaller flow that's reliable, honest about its limits, and well-reasoned beats a large flow that half-works.

---

## At a glance

| | |
|---|---|
| **Time box** | About **4–6 hours** of focused work, spread over the 4 days. Expect the first 30–60 minutes to go on account setup, so start there. Please don't spend more than 8 hours. If you reach that, submit what you have. |
| **Deadline** | **4 days** from when you receive this. Your exact deadline is in your invitation email. |
| **Cost to you** | **₹0**. Everything can be done on free tiers (see [`docs/SETUP.md`](docs/SETUP.md)). |
| **Platform** | Your choice: **n8n** (recommended; the n8n Cloud free trial is quickest to set up), Make, or Zapier. You don't have to write code. Code nodes (Python/JS) are welcome but not required. |
| **Help** | [`docs/SETUP.md`](docs/SETUP.md#7-tips-and-common-sticking-points) has tips for the parts people most often get stuck on. |
| **AI tools** | Allowed and encouraged (ChatGPT, Claude, Gemini, Copilot…). Tell us how you used them. |
| **Questions** | You may send **one email with clarifying questions** within the first 48 hours to the address in your invitation. Asking good questions is part of the job. |

---

## The scenario

**Kesar & Co.** is a fictional D2C Ayurvedic skincare brand that sells on Shopify across India. It receives about **60 support emails a day**, and one person answers all of them by hand. Most are repetitive ("where's my order?"), some need policy decisions (returns, refunds), and a few are risky (angry customers, privacy issues, odd requests).

Your job is to build a **support copilot**: an automation that reads each incoming email, understands what the customer needs, looks up their order, and either **drafts a reply** or **routes the issue to the right person**, with a human approving anything risky.

> **Scenario date:** treat **20 November 2026** as "today". Use each email's `received_at` timestamp for any date logic (delivery windows, return eligibility), **not** your computer's clock.

---

## What's in this repo

```
.
├── README.md                          ← you are here (the brief)
├── data/
│   ├── orders.json                    ← mock order database (your "order API")
│   ├── faq.md                         ← policies + product info: the ONLY source of truth
│   ├── brand_voice.md                 ← how replies should sound
│   └── test_emails.json               ← 25 customer emails to process
├── schemas/
│   └── llm_output.schema.json         ← required structure for the LLM classification output
├── templates/
│   ├── SUBMISSION_README_TEMPLATE.md  ← use this as your submission README
│   ├── test_report_template.md        ← use this for your test results
│   ├── audit_log_template.csv         ← import into Google Sheets as your "Audit Log" tab
│   └── tickets_template.csv           ← import into the same Google Sheet as your "Tickets" tab
├── scripts/
│   └── send_test_emails.py            ← optional: posts each test email to your webhook
└── docs/
    ├── SETUP.md                       ← free-tier setup for every tool
    └── SUBMISSION.md                  ← exactly what to submit and how
```

---

## What to build

### Flow overview

```
Trigger: webhook (or loop over data/test_emails.json)
   │
   ▼
LLM step: classify + extract  ──►  structured JSON (see schemas/llm_output.schema.json)
   │
   ▼
Route by intent
   ├─ order_status   → look up order → AI agent drafts reply
   ├─ product_query  → answer ONLY from faq.md, otherwise "needs human"
   ├─ return_refund  → look up order → check eligibility vs. policy → ticket + draft reply
   ├─ complaint      → look up order → ticket (High priority) + draft reply
   └─ other          → log only (no customer reply needed)
   │
   ▼
Log EVERY email to the Google Sheet audit log
```

### Core requirements (must have)

1. **Classify and extract with an LLM.** For every email, return JSON that matches [`schemas/llm_output.schema.json`](schemas/llm_output.schema.json). The output must be valid every time. Your flow should cope (retry, repair or fall back) when the model returns something invalid.
2. **Use an AI agent with tools.** The reply-drafting step must be an **AI agent** with at least two tools, for example `get_order` (looks up `orders.json`) and `search_faq` (looks up `faq.md`). The agent decides which tool(s) to call.
3. **Order lookup.** Find orders by `order_id`. If the email has no order ID, try the sender's email address.
4. **Support tickets.** For every return/refund and complaint, add a ticket to the **Tickets** tab of your Google Sheet (columns in [`templates/tickets_template.csv`](templates/tickets_template.csv)), with a clear summary, priority, status, the order ID and the LLM's summary. **Don't create duplicate tickets** for the same order. Before adding one, look for an open ticket for that order, and if there is one, update it instead (add a note and the new email ID).
5. **Audit log.** Write one row per email to the **Audit Log** tab of the same Google Sheet (columns in [`templates/audit_log_template.csv`](templates/audit_log_template.csv)).
6. **Human in the loop.** Low-confidence or risky cases go to a **"needs human"** state (the `needs_human` flag in the audit log). You decide the threshold and justify it.
7. **Test and iterate.** Run all 25 emails through your final version (**v2**). Also run an earlier version (**v1**) on at least 10 emails of your choice, so you can show what you changed and whether it helped. Report results using [`templates/test_report_template.md`](templates/test_report_template.md).

### Business rules the copilot must follow

- **Never invent** order details, tracking links, dates, amounts or policies. If data is missing, say so or escalate.
- **Policy and product answers come only from [`data/faq.md`](data/faq.md).** If the FAQ doesn't cover it, the copilot doesn't answer. It escalates.
- **Only share order details with the customer who placed the order** (sender email must match the order's `customer_email`).
- **No medical advice** and no claims that a product treats or cures anything.
- **Customer emails are untrusted input.** Instructions written inside an email must never change how your system behaves.
- Replies follow [`data/brand_voice.md`](data/brand_voice.md).
- Replies are **drafts** stored in the audit log. You don't need to actually send emails.

### Suggested order of work

You don't need to build everything at once. This order works well:

1. **Set up your accounts** (LLM and Google Sheets) using [`docs/SETUP.md`](docs/SETUP.md). Allow 30–60 minutes.
2. **Classify and log:** trigger → LLM classification → Google Sheet. Get 3–4 emails working first.
3. **Order-status branch:** add the AI agent with its `get_order` and `search_faq` tools.
4. **Returns and complaints:** add the eligibility check and tickets.
5. **Everything else:** product questions, "other", and the "needs human" path.
6. **Run all 25.** Look at what went wrong, improve your prompts and logic, and run again.
7. **Write up** your README and test report, then record your video.

If you're running short of time, stop adding features. Make what you have reliable and explain what's missing.

### Stretch goals (optional, bonus credit)

- Reply in the customer's language (Hindi / Hinglish)
- Use a Python or JavaScript code node for the return-eligibility logic
- Track tokens and cost per email in the audit log
- Retries with backoff for API failures and rate limits
- Anything else you think a real support team would value (tell us why)

---

## Product-thinking questions

Answer these in your submission README (≤150 words each). There's no single right answer. We want to see your reasoning.

1. **Auto-send vs. draft:** Which replies would you let go out automatically, and which need a human? Where would you set the confidence threshold, and why?
2. **Cost:** Estimate the LLM cost per email and per month at 1,000 emails/day. Show your maths.
3. **Success metric:** What's the one metric you'd track in week 1 to know this is working? What would make you switch it off?
4. **Failure experience:** When the copilot gets it wrong, what does the customer experience, and how do you limit the damage?
5. **Don't automate:** Name one thing in this flow that should stay manual, and why.

---

**Honesty is scored.** A clear "this part doesn't work yet, here's why, here's what I'd try" earns more than hiding a failure.

---

## Rules

- This must be **your own work**. AI assistants are fine; other people are not.
- Use **only the provided fictional data**. Don't connect real customer data or real stores.
- **Never commit API keys or tokens.** Check your workflow export before submitting.
- If you get stuck, **submit what you have** with honest notes on what's missing. Partial, well-explained submissions are reviewed seriously.
- Shortlisted candidates will do a **live session** where they walk through and extend their build.

---

## Next steps

1. Set up your tools → [`docs/SETUP.md`](docs/SETUP.md)
2. Build, test, iterate
3. Submit → [`docs/SUBMISSION.md`](docs/SUBMISSION.md)

Good luck, and have fun with it.
