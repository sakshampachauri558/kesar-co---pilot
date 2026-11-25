/**
 * audit_log_formatter.js
 * Prepares the exact 18-column row required by the "Audit Log" tab in Google Sheets.
 */
const item = $input.first().json;
const email = item.email || {};
const classification = item.classification || {};
const order = item.order || null;

const emailId = email.email_id || item.email_id;
const receivedAt = email.received_at || item.received_at;
const fromEmail = email.from_email || item.from_email;
const intent = classification.intent || 'other';
const secondaryIntent = classification.secondary_intent || '';
const orderId = order?.order_id || classification.order_id || '';
const language = classification.language || 'en';
const sentiment = classification.sentiment || 'neutral';
const confidence = classification.confidence !== undefined ? classification.confidence : 0;
const orderFound = item.order_found ? 'TRUE' : 'FALSE';

// Action taken description
let actionTaken = 'Draft reply generated';
if (intent === 'other' && !item.reply_draft) {
  actionTaken = 'Logged only (no reply needed)';
} else if (item.ticket_action === 'CREATE') {
  actionTaken = `Created ticket ${item.ticket_id} + drafted reply`;
} else if (item.ticket_action === 'UPDATE') {
  actionTaken = `Updated ticket ${item.ticket_id} + drafted reply`;
}

const needsHuman = item.needs_human ? 'TRUE' : 'FALSE';
const ticketId = item.ticket_id || '';
const replyDraft = item.reply_draft || '';
const promptVersion = 'v2';
const processedAt = new Date().toISOString();
const error = item.error || '';
const notes = (item.escalation_reasons && item.escalation_reasons.length > 0)
  ? item.escalation_reasons.join('; ')
  : (item.notes || 'Processed successfully');

return {
  json: {
    email_id: emailId,
    received_at: receivedAt,
    from_email: fromEmail,
    intent: intent,
    secondary_intent: secondaryIntent,
    order_id: orderId,
    language: language,
    sentiment: sentiment,
    confidence: confidence,
    order_found: orderFound,
    action_taken: actionTaken,
    needs_human: needsHuman,
    ticket_id: ticketId,
    reply_draft: replyDraft,
    prompt_version: promptVersion,
    processed_at: processedAt,
    error: error,
    notes: notes
  }
};
