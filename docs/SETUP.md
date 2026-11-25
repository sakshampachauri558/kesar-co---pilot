# Setup Guide (all free tiers)

Everything in this assignment can be done at **zero cost**. Free-tier limits change from time to time. If one option doesn't work for you, pick an alternative and mention it in your README.

> **Security first:** store every API key/token in your platform's **credentials manager** or a local `.env` file. Never paste keys directly into nodes that get exported, and never commit them. `.env` is already in `.gitignore`.

---

## 1. Automation platform (pick one)

| Option | How to get it | Notes |
|---|---|---|
| **n8n Cloud (easiest)** | Free trial at https://n8n.io | Nothing to install. Google sign-in for Sheets is one click, and webhook URLs are public out of the box. Check the trial lasts past your deadline, and past the live round if you're shortlisted. |
| **n8n — self-hosted** | Docker: `docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n` · or Node: `npx n8n` · then open http://localhost:5678 | Free, no limits. Connecting Google Sheets needs your own Google Cloud OAuth client (see §5). |
| **Make** | Free plan at https://www.make.com | Watch the monthly operations limit. Running 25 emails × several steps × 2 prompt versions adds up. |
| **Zapier** | Free plan at https://zapier.com | Free-plan limits on multi-step workflows may restrict you. Check before committing. |

Both n8n options have a built-in **AI Agent** node with tool support. Docs: https://docs.n8n.io

**Public URLs:** if an external service ever needs to call *into* your workflow (e.g., a webhook from another tool), a locally hosted instance needs a public URL. Use n8n Cloud or a tunnel such as `ngrok` or `cloudflared`.

---

## 2. LLM API (pick one, or mix)

| Option | Where |
|---|---|
| Google Gemini (free tier via AI Studio) | https://aistudio.google.com |
| Groq (free tier, fast open models) | https://console.groq.com |
| OpenRouter (some free models) | https://openrouter.ai |
| OpenAI / Anthropic | Only if you already have credits. Not required. |

You choose the model(s). Mention them and your settings (temperature, etc.) in your README. Using a cheaper/faster model for classification and a stronger one for drafting is a legitimate design choice. Just explain it.

---

## 3. Order "API" — `data/orders.json`

Treat this file as a **read-only order API**.

- **Easiest:** call this URL with an HTTP GET request, then filter the result by `order_id` or `customer_email` inside your workflow:
  https://raw.githubusercontent.com/abhishek-patel-cadient/kesar-ai-copilot-assignment/refs/heads/main/data/orders.json
- **Alternatives:** import the orders into a Google Sheet or Airtable, or serve the file locally (e.g., `npx json-server data/orders.json`). Any approach is fine if your `get_order` tool behaves like an API lookup.

Field reference (each order):

| Field | Meaning |
|---|---|
| `order_id` | `KC-####` |
| `customer_name`, `customer_email` | Who placed the order |
| `order_date` | Date the order was placed |
| `items[]` | `sku`, `name`, `qty`, `unit_price` |
| `subtotal`, `shipping_fee`, `cod_fee`, `total` | Amounts in INR |
| `payment_method` | `prepaid` or `cod` |
| `status` | `processing`, `shipped`, `out_for_delivery`, `delivered`, `cancelled` |
| `courier`, `tracking_url` | Courier partner and tracking link (null if not shipped) |
| `shipped_date`, `estimated_delivery`, `delivered_date` | Dates (null if not applicable) |
| `cancelled_date`, `cancellation_reason`, `refund_status` | Filled only for cancelled orders |
| `shipping_address` | Delivery address |

---

## 4. FAQ knowledge — `data/faq.md`

Your `search_faq` tool can be as simple or as sophisticated as you like: fetch the file and pass the relevant section (or all of it) to the agent, split it by headings, or put it in a vector store. Explain your choice. The key requirement is that answers stay **grounded** in this file.

- FAQ: https://raw.githubusercontent.com/abhishek-patel-cadient/kesar-ai-copilot-assignment/refs/heads/main/data/faq.md
- Brand voice (for the reply-drafting prompt): https://raw.githubusercontent.com/abhishek-patel-cadient/kesar-ai-copilot-assignment/refs/heads/main/data/brand_voice.md

---

## 5. Google Sheets (audit log + tickets)

1. Create a Google Sheet named **Kesar Support** with two tabs. Use File → Import → "Insert new sheet(s)" to bring in each template's column headers:
   - **Audit Log**: from [`templates/audit_log_template.csv`](../templates/audit_log_template.csv). One row per email.
   - **Tickets**: from [`templates/tickets_template.csv`](../templates/tickets_template.csv). One row per return/refund or complaint. This is your simple ticketing system:
     - `ticket_id`: any unique ID, e.g. `TKT-001`
     - `status`: e.g. `Open` or `Closed`; add others if you need them
     - `email_ids`: every email linked to this ticket
     - `notes`: updates added over time
2. You may add columns, but keep the existing ones.
3. **Connecting from n8n:** on n8n Cloud, use **Sign in with Google**. On self-hosted n8n you need a Google Cloud OAuth client. Follow https://docs.n8n.io/integrations/builtin/credentials/google/ (about 15–20 minutes).
4. Before submitting, set sharing to **"Anyone with the link can view"**.

---

## 6. Running the 25 test emails

You can trigger your flow in either of two ways:

**A. Webhook + sender script (closest to real life)**

```bash
# Python 3.8+, no extra packages needed
python scripts/send_test_emails.py --url <YOUR_WEBHOOK_URL>                # all 25, 5s apart
python scripts/send_test_emails.py --url <YOUR_WEBHOOK_URL> --only E01,E05  # a subset
python scripts/send_test_emails.py --url <YOUR_WEBHOOK_URL> --dry-run       # preview only
```

Each POST body is one email object exactly as in `data/test_emails.json`.

**B. Loop inside your workflow:** fetch this URL and iterate over `emails[]`:
https://raw.githubusercontent.com/abhishek-patel-cadient/kesar-ai-copilot-assignment/refs/heads/main/data/test_emails.json

Either is fine. Keep a **delay between emails** so you don't hit free-tier rate limits on your LLM.

---

## 7. Tips and common sticking points

- **Start with 3–4 emails, not all 25.** For example: `python scripts/send_test_emails.py --url <URL> --only E01,E02,E03`.
- **Getting valid JSON every time.** Keep the classification temperature at or near 0. In n8n, you can attach a **Structured Output Parser** (paste in the schema) to the LLM node, and wrap it in an **Auto-fixing Output Parser**, which asks the model to repair invalid output. Add a simple fallback for when it still fails, for example `intent: "other"` plus needs human.
- **Don't make the LLM do date maths or arithmetic.** Work out "days since delivery" from the email's `received_at` and the order's `delivered_date` in your workflow, then give the result to the LLM. In n8n, an expression like this works:
  `{{ Math.floor(DateTime.fromISO($json.received_at).diff(DateTime.fromISO($json.delivered_date), 'days').days) }}`
  A few lines in a Code node work too.
- **Agent tools.** Attach tools to the AI Agent node, for example an HTTP Request tool that fetches `orders.json`, or a Code tool. Give each tool a clear name and description. The agent chooses tools based on those descriptions.
- **Enforce hard rules in workflow logic, not only in prompts.** Rules about privacy, eligibility and not inventing data are safer as IF or Code checks, because a model can be talked out of them. Use the prompt for tone and wording.
- **Avoiding duplicate tickets.** Before adding a ticket, look in the Tickets tab for a row with the same `order_id` whose status isn't `Closed`. If you find one, update that row instead: add the new email ID to `email_ids` and append a note. In n8n, the Google Sheets node's **Get Row(s)** operation can filter on a column value, and **Update Row** changes an existing row.
- **Rate limits and flaky APIs.** Keep a few seconds between emails. In n8n, turn on **Retry On Fail** in the settings of your LLM and API nodes.
- **Exporting without secrets.** If your keys are stored as credentials (not typed into node fields), a normal n8n export won't contain them. Search the file anyway before you commit it.
