# Kesar & Co. Support Copilot — <Your Name>

> Copy this file into your submission as `README.md` and fill in every section. Keep it concise. Bullet points are fine.

## 1. Summary

- What I built (2–3 lines):
- Platform and LLM used:
- Time spent (approx. hours):
- What works / what doesn't:

## 2. Architecture

Add a screenshot of the full workflow and a short description of each major step or branch.

![workflow](./screenshots/workflow.png)

| Step / node | What it does | Why I designed it this way |
|---|---|---|
| | | |

## 3. Setup — how someone else can run this

1. Accounts/credentials needed (no actual keys!):
2. How to import the workflow:
3. Where to configure environment variables / credentials:
4. How to run the 25 test emails:

## 4. Prompts

Paste your final prompts (classification + agent/system prompt). Mention model settings (temperature, etc.).

## 5. Key decisions and assumptions

- How I handle low-confidence classifications:
- How I avoid duplicate tickets:
- How I make sure order details only go to the right customer:
- How I keep answers grounded in the FAQ:
- Other assumptions:

## 6. Scaling to 1,000 emails/day

What would break first, and what would you change? (rate limits, cost, queueing, monitoring, retries…)

## 7. Product-thinking questions (≤150 words each)

1. **Auto-send vs. draft:** Which replies would you let go out automatically, and which need a human? Where would you set the confidence threshold, and why?
2. **Cost:** Estimate the LLM cost per email and per month at 1,000 emails/day. Show your maths.
3. **Success metric:** What's the one metric you'd track in week 1 to know this is working? What would make you switch it off?
4. **Failure experience:** When the copilot gets it wrong, what does the customer experience, and how do you limit the damage?
5. **Don't automate:** Name one thing in this flow that should stay manual, and why.

## 8. How I used AI tools

Which AI tools you used while building (e.g., to write prompts, debug, generate code) and where you relied on your own judgment instead.

## 9. If I had one more week

-
