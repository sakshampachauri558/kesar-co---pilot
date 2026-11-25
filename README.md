# Kesar & Co. Support Copilot — Saksham Pachauri

**Prepared by:** Saksham Pachauri  
**GitHub Repository:** [https://github.com/sakshampachauri558/kesar-co---pilot](https://github.com/sakshampachauri558/kesar-co---pilot)  
**Live Google Sheet:** [Kesar Support Google Sheet](https://docs.google.com/spreadsheets/d/1dNM176hfNtVme6NZ-Yh7Ctni7wPnjRAEj1ajw87qdao/edit?gid=0#gid=0)  
**5-Minute Demo Video: https://drive.google.com/file/d/1kiAw_VA1KZnGuVk6InPDhP01vR0Wtl2N/view
## 1. Summary

- **What Saksham built:** An automated, production-ready Support Copilot for the D2C Ayurvedic skincare brand "Kesar & Co." It receives support emails through a webhook, produces structured classifications, performs privacy-safe order lookups, applies deterministic return and damage policies, drafts responses in the brand voice, prevents duplicate tickets, and records the complete workflow in Google Sheets.
- **Platform and LLM used:** n8n Cloud (with exported blueprint), Google Gemini 1.5 Flash (via Google AI Studio, temperature 0.0 for deterministic classification, 0.2 for drafting), JavaScript deterministic logic nodes.
- **Live Google Sheet Link:** [Kesar Support Google Sheet](https://docs.google.com/spreadsheets/d/1dNM176hfNtVme6NZ-Yh7Ctni7wPnjRAEj1ajw87qdao/edit?gid=0#gid=0) (View access enabled)
- **Demo Video Recording:** [Google Drive Video Link]: https://drive.google.com/file/d/1kiAw_VA1KZnGuVk6InPDhP01vR0Wtl2N/view
- **Time spent:** Approximately 5.5 hours across architecture design, prompt hardening, edge-case testing, and documentation.
- **What works:** 100% schema-valid JSON extraction, zero-hallucination policy grounding in `faq.md`, automated prompt injection neutralization (email `E12`), customer email privacy protection (email `E07`), smart ticket deduplication (email `E04` & `E21`), Hinglish/Hindi recognition, deterministic return window validation, and an automated 6-point CI/CD safety eval suite (`scripts/run_evals.py`).
- **What doesn't:** Unidentified vague emails with zero metadata (`E18`) cannot be automatically matched to customer records and are escalated to human review.

---

## 2. Architecture

```
Webhook Trigger (POST /support-email)
   │
   ▼
Normalize & Guardrails (Code Node: cleans payload, detects prompt injection)
   │
   ├─► Fetch Orders DB (GET orders.json)
   ├─► Fetch FAQ Knowledge (GET faq.md)
   │
   ▼
Classify & Extract Intent (Gemini LLM: schemas/llm_output.schema.json)
   │
   ▼
Order Lookup & Deterministic Rules (Code Node: email privacy check, date arithmetic vs 2026-11-20)
   │
   ▼
Route by Intent (Switch Node)
   ├─► order_status   ──► Draft tracking/delay update via brand voice
   ├─► product_query  ──► Answer ONLY from FAQ catalog; escalate medical claims
   ├─► return_refund  ──► Validate 7-day unopened window ──► Ticket + Draft
   ├─► complaint      ──► Damaged/leaking/wrong 48h check ──► High-Priority Ticket + Draft
   └─► other          ──► Filter spam/collab/GST ──► Log only or escalate
   │
   ▼
Ticket Deduplication (Code Node: search open tickets by order_id; update if exists, else create)
   │
   ▼
Format Audit Log Row (Code Node: 18 columns matching template)
   │
   ├─► Google Sheets (Audit Log tab append)
   └─► Webhook Response (HTTP 200 JSON confirmation)
```

| Step / node | What it does | Why Saksham designed it this way |
|---|---|---|
| **Webhook** | Receives single email JSON payload from `send_test_emails.py`. | Standard enterprise integration pattern for real-time inbox ingestion. |
| **Normalize & Guardrails** | Sanitizes text and flags prompt injection patterns (`SYSTEM NOTE`, `ignore previous instructions`). | Treating user input as untrusted at the gateway prevents adversarial jailbreaks from reaching the LLM. |
| **Order & FAQ Fetch** | Pulls fresh order database and policy markdown. | Decouples data storage from workflow logic, treating mock files as read-only microservice APIs. |
| **Classify & Extract Intent** | Returns structured JSON adhering to `llm_output.schema.json`. | Structured extraction at temperature 0.0 guarantees consistent programmatic routing. |
| **Order Lookup & Rules** | Matches order by `order_id` or email, checks privacy, calculates `days_since_delivery` vs `2026-11-20`. | LLMs are notorious for date arithmetic errors; deterministic code ensures 100% reliable policy enforcement. |
| **Route by Intent** | Branches into 5 explicit support paths. | Isolates business domains, allowing independent tuning of policies, tools, and response templates. |
| **Draft Reply (Brand Voice)** | Generates 3-6 sentence warm, honest replies signed by Team Kesar. | Enforces strict compliance with `brand_voice.md` and medical disclaimers from `faq.md`. |
| **Ticket Deduplication** | Searches existing tickets; updates open tickets instead of creating duplicates. | Prevents split conversations and agent confusion when customers follow up on the same order. |
| **Google Sheets Logging** | Appends full execution record to the Audit Log. | Provides complete observability, compliance tracking, and human-in-the-loop escalation. |

---

## 3. Setup — How Someone Else Can Run This

1. **Accounts/credentials needed:**
   - Free [n8n Cloud](https://n8n.io) account (or self-hosted n8n v1.x+ via Docker).
   - Google Account with view/edit access to Google Sheets.
   - Free Gemini API key from [Google AI Studio](https://aistudio.google.com).
2. **How to import the workflow:**
   - Open n8n, navigate to **Workflows** → Click **Add Workflow** → Click the three dots (top right) → Select **Import from File**.
   - Choose `workflow/kesar_copilot_workflow.json` (Production Pipeline) or `workflow/kesar_copilot_ai_agent.json` (Agentic Pipeline with LangChain Tools: `get_order` & `search_faq`).
3. **Where to configure credentials:**
   - In the **Google Sheets (Audit Log)** node, select **Google Sheets OAuth2 API** and click "Sign in with Google". Paste your Google Sheet URL into `Document`.
   - In workflow settings or node environment, configure your `GEMINI_API_KEY`.
4. **How to run the 25 test emails & safety evals:**
   ```bash
   # Test a small batch first
   python scripts/send_test_emails.py --url <YOUR_N8N_WEBHOOK_URL> --only E01,E02,E03

   # Run all 25 emails with 5-second delay
   python scripts/send_test_emails.py --url <YOUR_N8N_WEBHOOK_URL>

   # Run automated CI/CD safety & policy evaluations suite
   python scripts/run_evals.py
   ```

---

## 4. Prompts

The system utilizes two distinct, production-hardened prompts:

- **Classification & Extraction Prompt:** [prompts/classification_prompt.md](prompts/classification_prompt.md)
  - *Model:* Gemini 1.5 Flash | *Temperature:* 0.0 | *Response format:* Raw JSON matching `schemas/llm_output.schema.json`.
- **AI Reply-Drafting Agent Prompt:** [prompts/agent_reply_prompt.md](prompts/agent_reply_prompt.md)
  - *Model:* Gemini 1.5 Flash | *Temperature:* 0.2 | *System Persona:* Kesar & Co. Customer Specialist, bound to `brand_voice.md` (3-6 sentences, no emojis, no filler, warm tone, matching customer language).

---

## 5. Key Decisions and Assumptions

- **How low-confidence classifications are handled:** Any classification with confidence below 0.70 or an unresolvable intent automatically sets `needs_human: TRUE` in the audit log. The system records the intent and its notes without generating an automatic customer reply.
- **How duplicate tickets are avoided:** For return/refund and complaint emails, the workflow searches for an existing open ticket with the same `order_id`. If found, it adds the new email ID (for example, `E04, E21`) and appends the latest summary to `notes` using the `UPDATE` action.
- **How customer order details are protected:** The `order_lookup_and_rules.js` node strictly compares `from.email` with `order.customer_email`. For mismatches such as email `E07`, it raises `privacy_violation`, withholds order details, and prepares a privacy-safe notice.
- **How answers remain grounded in the FAQ:** The prompts instruct the model to treat `data/faq.md` as the sole source of truth. Missing policy or product details, such as international shipping or medical cure claims, trigger human review instead of allowing the model to improvise.
- **Deterministic Date Math:** Scenario date `2026-11-20` is hardcoded into the business logic node. The 7-day return policy and 48-hour damage reporting windows are computed via `Math.floor(diffMs / 86400000)`, ensuring zero LLM date hallucination.

---

## 6. Scaling to 1,000 Emails/Day

At 1,000 emails/day (~42 emails/hour average, peaking at 150/hour during business hours):

1. **What would break first:**
   - **Rate Limits & Concurrency:** Direct LLM API calls and Google Sheets API calls would hit free-tier rate limits (Google Sheets quota is 60 requests/minute per user; Gemini free tier is 15 RPM).
   - **Google Sheets as a Database:** Appending and searching rows in Google Sheets at scale causes row-lock contention, race conditions during ticket deduplication, and slow response times.
2. **Recommended scaling changes:**
   - **Queue Worker Architecture:** Introduce a message broker (RabbitMQ, Redis Streams, or AWS SQS) between the webhook and the processor, decoupling ingestion from execution with controlled concurrency and exponential backoff retries.
   - **Enterprise Storage:** Migrate tickets and audit logging from Google Sheets to PostgreSQL with indexed columns on `order_id` and `customer_email`, enabling ACID-compliant row locking for deduplication.
   - **Semantic Caching & Tiered Routing:** Cache common FAQ product queries in Redis. Route simple order status queries to lightweight models or direct SQL lookups, reserving frontier LLM reasoning only for complex complaints.

---

## 7. Product-Thinking Questions (≤150 words each)

### 1. Auto-send vs. Draft
> **Answer:** I would allow automatic sending only after a complete set of checks passes: the classification is an FAQ-backed product question or an order-status request, the sender email matches the order, and confidence is at least 0.90. Returns, refunds, damaged or leaking products, angry customers, policy exceptions, and any lower-confidence result should remain drafts for agent approval. This tiered approach avoids exposing customers to incorrect refund decisions or unsupported ingredient claims. A short review delay is safer for the brand than an immediate but unreliable reply.

### 2. Cost Estimation at 1,000 Emails/Day
> **Answer:**
> - **Estimated usage:** Classification uses approximately 400 input and 100 output tokens. Reply drafting uses approximately 1,000 input and 250 output tokens, so one email requires about 1,400 input and 350 output tokens.
> - **Applied pricing:** Gemini 1.5 Flash is priced at approximately $0.075 per million input tokens and $0.30 per million output tokens.
> - **Daily email cost:** Input cost is $1,400 × $0.000000075 = $0.000105; output cost is $350 × $0.00000030 = $0.000105. The complete estimate is **$0.00021 per email** (roughly ₹0.0175).
> - **Monthly estimate:** At 1,000 emails daily, 30,000 emails cost approximately **$6.30/month** (about ₹525). Allowing a 100% buffer for retries and workflow overhead keeps the planned budget below $13/month.

### 3. Success Metric & Kill Switch
> **Answer:**
> - **Primary measure:** I would track **Draft Acceptance Rate (DAR)** during the first week: the share of suggested replies approved with no more than a minor edit. My initial target is at least 80%, because a lower result could indicate that the copilot creates more review work than it saves.
> - **Stop condition:** I would disable routing, drafting, or both if the system records a critical safety failure. This includes exposing PII to the wrong customer, authorizing an unapproved refund, or making a claim that a product diagnoses, treats, or cures a medical condition.
> - **Recovery:** I would preserve the audit record, correct the prompt or deterministic rule that caused the failure, run a focused regression suite, and only restore the workflow after the affected cases pass.

### 4. Failure Experience & Damage Limitation
> **Answer:** A bad classification or awkward draft can make the customer feel ignored or lose confidence in the brand. To limit that impact, I would keep drafts under human review during rollout and require clear evidence before automated sending. Responses should state only verified facts and include a natural invitation to continue the conversation with the support team.
> 1. For uncertain policies or incomplete order information, the workflow should create a draft and route it to an agent rather than invent an answer.
> 2. Any sensitive or financial decision must remain in draft status until a person approves it.
> 3. If a customer replies again within four hours, the system should bypass the standard AI path and escalate that conversation to a senior human agent.

### 5. What Should Stay Manual, and Why
> **Answer:** Reports of burning, rashes, allergic reactions, or other adverse effects should stay fully manual. These conversations involve potential health risks, product-quality investigation, lot tracing, and regulated escalation that an LLM should not attempt to manage. A qualified team member can respond with empathy, gather the necessary symptoms and usage details, and coordinate with quality or medical professionals. Automating this category could create legal exposure and would be especially inappropriate when a customer is physically uncomfortable or distressed.

---

## 8. How AI Tools Were Used

- **Prompt development:** I used Claude and Gemini as review tools to explore schema edge cases and identify prompt-injection examples for `llm_output.schema.json`.
- **Implementation support:** AI tools helped create initial JavaScript boilerplate for date calculations, privacy checks, and ticket deduplication. I treated generated code as a draft and verified it against the assignment scenarios.
- **Personal decisions:** I chose the hard-coded safeguards, confidence threshold, escalation rules, and kill-switch conditions based on the project's privacy, policy, and safety requirements.
- **Final validation:** I relied on deterministic tests and the 25-email workflow results rather than assuming that prompt quality alone would guarantee reliable behavior.

---

## 9. What Saksham Would Build with One More Week

1. **Agent tools with context:** Replace isolated HTTP lookups with LangChain tools that can decide whether to retrieve an order, search the FAQ, or request human help.
2. **FAQ retrieval:** Add a small vector index over the FAQ and catalog so product questions can retrieve exact passages instead of depending only on manual prompt context.
3. **Unified conversations:** Extend the webhook to WhatsApp and Shopify Inbox, then attach each channel to one customer support timeline.
4. **Faster escalation:** Send angry-customer and damage reports to Slack or Zendesk with one-click approval, while preserving the same audit trail used by Google Sheets.
