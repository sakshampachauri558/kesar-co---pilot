/**
 * normalize_and_sanitize.js
 * Runs right after the Webhook trigger to sanitize input and detect prompt injections.
 */
const input = $input.first().json;
const email = input.body || input; // Handle either nested body or direct payload

const emailId = email.id || 'E00';
const receivedAt = email.received_at || '2026-11-20T00:00:00+05:30';
const fromObj = email.from || {};
const fromName = fromObj.name || 'Customer';
const fromEmail = (fromObj.email || '').trim().toLowerCase();
const subject = email.subject || '';
const body = email.body || '';

// Security: Detect prompt injection / jailbreak patterns in untrusted email body
const injectionRegex = /(ignore all previous instructions|system note|you are now|override policy|mark.*approved|vip customer)/i;
const promptInjectionDetected = injectionRegex.test(body);

return {
  json: {
    email_id: emailId,
    received_at: receivedAt,
    from_name: fromName,
    from_email: fromEmail,
    subject: subject,
    body: body,
    prompt_injection_detected: promptInjectionDetected,
    scenario_today: '2026-11-20'
  }
};
