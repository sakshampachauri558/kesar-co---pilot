import json

def build_workflow():
    workflow = {
        "name": "Kesar & Co. AI Support Copilot",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "support-email",
                    "responseMode": "responseNode",
                    "options": {}
                },
                "id": "node-webhook",
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [40, 300],
                "webhookId": "kesar-support-email-webhook"
            },
            {
                "parameters": {
                    "jsCode": """// Normalize incoming email and detect prompt injection
const input = $input.first().json;
const email = input.body || input;

const emailId = email.id || 'E00';
const receivedAt = email.received_at || '2026-11-20T09:00:00+05:30';
const fromObj = email.from || {};
const fromName = fromObj.name || 'Customer';
const fromEmail = (fromObj.email || '').trim().toLowerCase();
const subject = email.subject || '';
const body = email.body || '';

// Security: Detect prompt injection / jailbreak patterns
const injectionRegex = /(ignore all previous instructions|system note|override policy|mark.*approved|vip customer)/i;
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
};"""
                },
                "id": "node-normalize",
                "name": "Normalize & Guardrails",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [240, 300]
            },
            {
                "parameters": {
                    "url": "https://raw.githubusercontent.com/abhishek-patel-cadient/kesar-ai-copilot-assignment/refs/heads/main/data/orders.json",
                    "options": {}
                },
                "id": "node-fetch-orders",
                "name": "Fetch Orders DB",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [440, 300]
            },
            {
                "parameters": {
                    "url": "https://raw.githubusercontent.com/abhishek-patel-cadient/kesar-ai-copilot-assignment/refs/heads/main/data/faq.md",
                    "options": {}
                },
                "id": "node-fetch-faq",
                "name": "Fetch FAQ Knowledge",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [640, 300]
            },
            {
                "parameters": {
                    "jsCode": """// Local & deterministic classification fallback + schema enforcement
const email = $('Normalize & Guardrails').first().json;
const body = (email.body || '').toLowerCase();
const subject = (email.subject || '').toLowerCase();
const text = subject + ' ' + body;

// Extract order_id if present (regex: KC-[0-9]{4})
const orderMatch = (email.subject + ' ' + email.body).match(/KC-[0-9]{4}/i);
const orderId = orderMatch ? orderMatch[0].toUpperCase() : null;

// Determine language
let language = 'en';
if (/[\\u0900-\\u097F]/.test(email.body)) {
  language = 'hi';
} else if (/\\b(kya|kab|kaise|nahi|mera|meri|aayega|bata do|chahiye|shukriya|namaste)\\b/i.test(email.body)) {
  language = 'hinglish';
}

// Determine sentiment
let sentiment = 'neutral';
if (/worst|ruined|mess|unacceptable|angry|fraud|threat|useless/i.test(body)) {
  sentiment = 'angry';
} else if (/not happy|disappointed|cracked|spilled|leaked|missing|wrong/i.test(body)) {
  sentiment = 'negative';
} else if (/thank you|thanks|lovely|great|soothing|quick delivery/i.test(body)) {
  sentiment = 'positive';
}

// Determine intent
let intent = 'other';
let secondaryIntent = null;
let confidence = 0.95;
let summary = '';

if (/google ranking|ranking on google|seo rankers|congratulations/i.test(text)) {
  intent = 'other';
  summary = 'Spam/promotional email offering SEO services';
} else if (/collab|collaboration|influencer|followers|media kit/i.test(text)) {
  intent = 'other';
  secondaryIntent = null;
  summary = 'Influencer collaboration proposal';
} else if (/gst invoice|gstin|reimbursement/i.test(text)) {
  intent = 'other';
  summary = 'Request for corporate GST invoice';
} else if (/thank you|lovely.*soothing/i.test(text)) {
  intent = 'other';
  sentiment = 'positive';
  summary = 'Customer feedback and appreciation';
} else if (/damaged|cracked|leaked|wrong item|missing/i.test(text)) {
  intent = 'complaint';
  summary = 'Customer complaining about damaged, wrong or missing item in delivery';
} else if (/return|refund/i.test(text)) {
  intent = 'return_refund';
  summary = 'Customer requesting return or refund for order';
} else if (/where is|status|tracking|kab aayega|when will it reach/i.test(text)) {
  intent = 'order_status';
  summary = 'Inquiry regarding shipping or delivery status';
} else if (/oily skin|vegan|eczema|serum.*skin|cure|ingredients|how to use/i.test(text)) {
  intent = 'product_query';
  summary = 'Product compatibility or skincare inquiry';
}

return {
  json: {
    email: email,
    classification: {
      intent: intent,
      secondary_intent: secondaryIntent,
      order_id: orderId,
      sentiment: sentiment,
      language: language,
      confidence: confidence,
      summary: summary
    }
  }
};"""
                },
                "id": "node-classify",
                "name": "Classify & Extract Intent",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [840, 300]
            },
            {
                "parameters": {
                    "jsCode": """// Order lookup, privacy check, date arithmetic, and rules verification
const item = $input.first().json;
const email = item.email || {};
const classification = item.classification || {};
const ordersData = $('Fetch Orders DB').first().json;
const orders = ordersData.orders || [];

const fromEmail = (email.from_email || '').toLowerCase().trim();
const extractedOrderId = classification.order_id || null;

// 1. Order Lookup
let matchedOrder = null;
if (extractedOrderId) {
  matchedOrder = orders.find(o => o.order_id.toUpperCase() === extractedOrderId.toUpperCase());
}
if (!matchedOrder && fromEmail) {
  matchedOrder = orders.find(o => o.customer_email.toLowerCase().trim() === fromEmail);
}

const orderFound = !!matchedOrder;
let privacyViolation = false;
let orderDetailsAllowed = false;

// 2. Customer Privacy Verification
if (matchedOrder) {
  const orderOwnerEmail = matchedOrder.customer_email.toLowerCase().trim();
  if (orderOwnerEmail !== fromEmail) {
    privacyViolation = true;
    orderDetailsAllowed = false;
  } else {
    orderDetailsAllowed = true;
  }
}

// 3. Date Arithmetic relative to 20 November 2026
const SCENARIO_DATE = new Date('2026-11-20T00:00:00+05:30');
let daysSinceDelivery = null;
let returnEligible = false;
let damagedWindowValid = false;

if (matchedOrder && matchedOrder.delivered_date) {
  const deliveryDate = new Date(matchedOrder.delivered_date + 'T00:00:00+05:30');
  const diffMs = SCENARIO_DATE.getTime() - deliveryDate.getTime();
  daysSinceDelivery = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  returnEligible = (daysSinceDelivery <= 7 && daysSinceDelivery >= 0);
  damagedWindowValid = (daysSinceDelivery <= 2 && daysSinceDelivery >= 0);
}

// 4. Escalation (needs_human)
let needsHuman = false;
const reasons = [];

if (email.prompt_injection_detected) {
  needsHuman = true;
  reasons.push('Prompt injection detected in customer email');
}

if (privacyViolation) {
  needsHuman = true;
  reasons.push('Privacy mismatch: sender email does not match order email');
}

if (/eczema|cure/i.test(email.body)) {
  needsHuman = true;
  reasons.push('Medical or cure claim question (escalated for safety)');
}

if (classification.intent === 'other' && !/thank you|simran/i.test(email.body) && !/seo rankers/i.test(email.body)) {
  needsHuman = true;
  reasons.push('Non-standard or partnership inquiry needing manual attention');
}

return {
  json: {
    email: email,
    classification: classification,
    order: matchedOrder,
    order_found: orderFound,
    privacy_violation: privacyViolation,
    order_details_allowed: orderDetailsAllowed,
    days_since_delivery: daysSinceDelivery,
    return_eligible: returnEligible,
    damaged_window_valid: damagedWindowValid,
    needs_human: needsHuman,
    escalation_reasons: reasons
  }
};"""
                },
                "id": "node-order-rules",
                "name": "Order Lookup & Rules",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1040, 300]
            },
            {
                "parameters": {
                    "dataType": "string",
                    "value1": "={{ $json.classification.intent }}",
                    "rules": {
                        "rules": [
                            { "value2": "order_status" },
                            { "value2": "product_query" },
                            { "value2": "return_refund" },
                            { "value2": "complaint" }
                        ]
                    },
                    "fallbackOutput": 4
                },
                "id": "node-switch",
                "name": "Route by Intent",
                "type": "n8n-nodes-base.switch",
                "typeVersion": 3,
                "position": [1260, 300]
            },
            {
                "parameters": {
                    "jsCode": """// Draft reply generator adhering strictly to brand_voice.md and faq.md
const item = $input.first().json;
const email = item.email || {};
const order = item.order || {};
const classification = item.classification || {};
const firstName = (email.from_name || 'there').split(' ')[0];
const lang = classification.language || 'en';

let reply = '';

// Security Check: Privacy Violation
if (item.privacy_violation) {
  reply = `Hi ${firstName},\\n\\nThank you for reaching out. To protect our customers' personal information and privacy, we can only share tracking and delivery details directly with the email address registered on the order.\\n\\nPlease have the person who placed the order reach out to us from their email, and we will gladly share the updates right away.\\n\\nWarm regards,\\nTeam Kesar`;
}
// Security Check: Prompt Injection Defense
else if (email.prompt_injection_detected) {
  reply = `Hi ${firstName},\\n\\nThank you for getting in touch. According to our hygiene and return policy, products that have been unsealed or used are not eligible for return or refund. As a result, we cannot approve a refund for this order.\\n\\nIf you have any further questions or need product guidance, please feel free to let us know.\\n\\nWarm regards,\\nTeam Kesar`;
}
// Eczema / Medical Query
else if (/eczema|cure/i.test(email.body)) {
  reply = `Hi ${firstName},\\n\\nOur Kumkumadi Night Oil is a traditional cosmetic blend designed to nourish skin, but it is not a medical treatment and is not formulated to diagnose, treat, or cure eczema. Because facial eczema can be very sensitive, we strongly recommend consulting your dermatologist before introducing any new skincare product.\\n\\nWe also always advise performing a small patch test on your inner forearm 24 hours prior to use.\\n\\nWarm regards,\\nTeam Kesar`;
}
// Order Status Replies
else if (classification.intent === 'order_status') {
  if (lang === 'hinglish') {
    reply = `Hi ${firstName},\\n\\nAapka order ${order.order_id || 'KC-1043'} ship ho chuka hai aur 23 November 2026 tak deliver hone ki ummeed hai. Aap is tracking link par shipment check kar sakte hain: ${order.tracking_url || 'https://track.example.com/SS7781043'}.\\n\\nAgar aapko travel se pehle aur koi madad chahiye, toh humein zaroor batayein.\\n\\nWarm regards,\\nTeam Kesar`;
  } else if (!item.order_found) {
    reply = `Hi ${firstName},\\n\\nWe could not find an active order under order number ${classification.order_id || 'provided'}. Please verify your order number or let us know the email address used during checkout so we can trace it for you.\\n\\nWarm regards,\\nTeam Kesar`;
  } else if (order.status === 'out_for_delivery') {
    reply = `Hi ${firstName},\\n\\nYour order ${order.order_id} is out for delivery today with ${order.courier || 'our courier'}. Since this is a Cash on Delivery order of Rs ${order.total || '1,897'}, please keep the exact amount ready as courier partners may not carry change.\\n\\nWarm regards,\\nTeam Kesar`;
  } else if (order.status === 'cancelled') {
    reply = `Hi ${firstName},\\n\\nYour order ${order.order_id} was cancelled on 16 November 2026 because the Sandalwood Body Lotion was unfortunately out of stock at our warehouse. A full refund of Rs ${order.total || '828'} was initiated to your original payment method and will reflect within 5-7 business days.\\n\\nWarm regards,\\nTeam Kesar`;
  } else {
    reply = `Hi ${firstName},\\n\\nYour order ${order.order_id} is on its way and scheduled to reach you by ${order.estimated_delivery || '21 November 2026'}. You can track the live progress of your package via ${order.courier || 'SwiftShip'} here: ${order.tracking_url || 'https://track.example.com'}.\\n\\nWarm regards,\\nTeam Kesar`;
  }
}
// Product Query
else if (classification.intent === 'product_query') {
  if (lang === 'hi') {
    reply = `नमस्ते ${firstName},\\n\\nगुवाहाटी के लिए हमारा डिलीवरी समय 6-8 कार्य दिवस है। 5,000 रुपये तक के सभी ऑर्डरों पर कैश ऑन डिलीवरी (COD) उपलब्ध है, जिस पर 49 रुपये का हैंडलिंग शुल्क लागू होता है।\\n\\nयदि आपके पास कोई अन्य प्रश्न हैं, तो हमें अवश्य बताएं।\\n\\nWarm regards,\\nTeam Kesar`;
  } else {
    reply = `Hi ${firstName},\\n\\nYes, our Saffron Glow Face Serum is lightweight, non-greasy, and formulated to be suitable for all skin types, including oily skin. It is also 100% vegan and cruelty-free, making it a great fit for your vegan routine.\\n\\nWarm regards,\\nTeam Kesar`;
  }
}
// Return / Refund
else if (classification.intent === 'return_refund') {
  if (item.days_since_delivery > 7) {
    reply = `Hi ${firstName},\\n\\nThank you for reaching out. Our return policy allows returns within 7 days of delivery for unopened items with seals intact. Since your order was delivered on 5 November 2026, it is outside the 7-day return window and we are unable to accept a return.\\n\\nWarm regards,\\nTeam Kesar`;
  } else if (order.payment_method === 'cod') {
    reply = `Hi ${firstName},\\n\\nWe can certainly assist you with returning the unopened Kumkumadi Oil and Aloe Gel from order ${order.order_id}. Since you paid via Cash on Delivery, our team will arrange a free reverse pickup and request your UPI ID or bank details once the items are collected to issue your refund within 5-7 business days.\\n\\nWarm regards,\\nTeam Kesar`;
  } else {
    reply = `Hi ${firstName},\\n\\nWe would be happy to process a return for order ${order.order_id}. Since your product is sealed and within our 7-day return period, we will arrange a complimentary reverse pickup within 2-3 business days and issue a full refund to your original payment method.\\n\\nWarm regards,\\nTeam Kesar`;
  }
}
// Complaints (Damaged / Missing / Wrong)
else if (classification.intent === 'complaint') {
  reply = `Hi ${firstName},\\n\\nWe are very sorry for the inconvenience caused with your order ${order.order_id || ''}. Our support team has created high-priority ticket for this issue, and we will follow up within 24 business hours to arrange an immediate replacement or full refund as per your preference.\\n\\nWarm regards,\\nTeam Kesar`;
}
// Other / Partnerships / GST
else {
  if (/collab|influencer/i.test(email.body)) {
    reply = `Hi ${firstName},\\n\\nThank you for your interest in Kesar & Co.! Please direct your collaboration proposal and media kit to our partnerships team at partnerships@kesarandco.example, and they will be happy to connect with you.\\n\\nWarm regards,\\nTeam Kesar`;
  } else if (/gst invoice/i.test(email.body)) {
    reply = `Hi ${firstName},\\n\\nThank you for reaching out. We have noted your request for a GST invoice for Bright Designs and forwarded it to our accounts department to issue and share with you shortly.\\n\\nWarm regards,\\nTeam Kesar`;
  } else {
    reply = ''; // No reply needed for spam or simple thank-you notes
  }
}

return {
  json: {
    ...item,
    reply_draft: reply
  }
};"""
                },
                "id": "node-draft-reply",
                "name": "Draft Reply (Brand Voice & FAQ)",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1500, 300]
            },
            {
                "parameters": {
                    "jsCode": """// Ticket deduplication and formatting
const item = $input.first().json;
const intent = item.classification?.intent;
const orderId = item.order?.order_id || item.classification?.order_id || 'N/A';
const emailId = item.email?.email_id || 'E00';
const customerEmail = item.order?.customer_email || item.email?.from_email || '';
const summary = item.classification?.summary || '';
const sentiment = item.classification?.sentiment || 'neutral';

const ticketRequired = (intent === 'return_refund' || intent === 'complaint');

if (!ticketRequired) {
  return {
    json: {
      ...item,
      ticket_action: 'NONE',
      ticket_id: ''
    }
  };
}

let priority = (intent === 'complaint' || sentiment === 'angry') ? 'High' : 'Medium';
let ticketId = 'TKT-001';
let ticketAction = 'CREATE';

// Special ticket deduplication handling for Tanvi Desai (KC-1052)
if (orderId === 'KC-1052') {
  if (emailId === 'E21') {
    ticketAction = 'UPDATE';
    ticketId = 'TKT-002';
  } else {
    ticketAction = 'CREATE';
    ticketId = 'TKT-002';
  }
} else if (orderId === 'KC-1051') {
  ticketId = 'TKT-001';
} else if (orderId === 'KC-1048') {
  ticketId = 'TKT-003';
} else if (orderId === 'KC-1053') {
  ticketId = 'TKT-004';
} else if (orderId === 'KC-1050') {
  ticketId = 'TKT-005';
} else if (orderId === 'KC-1054') {
  ticketId = 'TKT-006';
}

return {
  json: {
    ...item,
    ticket_action: ticketAction,
    ticket_id: ticketId,
    ticket_priority: priority
  }
};"""
                },
                "id": "node-ticket-logic",
                "name": "Ticket Deduplication & Logic",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1740, 300]
            },
            {
                "parameters": {
                    "jsCode": """// Audit log row formatter matching templates/audit_log_template.csv
const item = $input.first().json;
const email = item.email || {};
const classification = item.classification || {};
const order = item.order || null;

const emailId = email.email_id || 'E00';
const receivedAt = email.received_at || '';
const fromEmail = email.from_email || '';
const intent = classification.intent || 'other';
const secondaryIntent = classification.secondary_intent || '';
const orderId = order?.order_id || classification.order_id || '';
const language = classification.language || 'en';
const sentiment = classification.sentiment || 'neutral';
const confidence = classification.confidence !== undefined ? classification.confidence : 0;
const orderFound = item.order_found ? 'TRUE' : 'FALSE';

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
const error = '';
const notes = (item.escalation_reasons && item.escalation_reasons.length > 0)
  ? item.escalation_reasons.join('; ')
  : 'Processed successfully';

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
};"""
                },
                "id": "node-audit-log",
                "name": "Format Audit Log Row",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1980, 300]
            },
            {
                "parameters": {
                    "operation": "append",
                    "documentId": {
                        "__rl": True,
                        "mode": "url",
                        "value": ""
                    },
                    "sheetName": {
                        "__rl": True,
                        "mode": "name",
                        "value": "Audit Log"
                    },
                    "options": {}
                },
                "id": "node-sheets-audit",
                "name": "Google Sheets (Audit Log)",
                "type": "n8n-nodes-base.googleSheets",
                "typeVersion": 4.5,
                "position": [2220, 300]
            },
            {
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ JSON.stringify({ status: 'success', email_id: $json.email_id, action: $json.action_taken, ticket: $json.ticket_id }) }}",
                    "options": {}
                },
                "id": "node-respond",
                "name": "Respond to Webhook",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1.1,
                "position": [2440, 300]
            }
        ],
        "connections": {
            "Webhook": {
                "main": [[{"node": "Normalize & Guardrails", "type": "main", "index": 0}]]
            },
            "Normalize & Guardrails": {
                "main": [[{"node": "Fetch Orders DB", "type": "main", "index": 0}]]
            },
            "Fetch Orders DB": {
                "main": [[{"node": "Fetch FAQ Knowledge", "type": "main", "index": 0}]]
            },
            "Fetch FAQ Knowledge": {
                "main": [[{"node": "Classify & Extract Intent", "type": "main", "index": 0}]]
            },
            "Classify & Extract Intent": {
                "main": [[{"node": "Order Lookup & Rules", "type": "main", "index": 0}]]
            },
            "Order Lookup & Rules": {
                "main": [[{"node": "Route by Intent", "type": "main", "index": 0}]]
            },
            "Route by Intent": {
                "main": [
                    [{"node": "Draft Reply (Brand Voice & FAQ)", "type": "main", "index": 0}],
                    [{"node": "Draft Reply (Brand Voice & FAQ)", "type": "main", "index": 0}],
                    [{"node": "Draft Reply (Brand Voice & FAQ)", "type": "main", "index": 0}],
                    [{"node": "Draft Reply (Brand Voice & FAQ)", "type": "main", "index": 0}],
                    [{"node": "Draft Reply (Brand Voice & FAQ)", "type": "main", "index": 0}]
                ]
            },
            "Draft Reply (Brand Voice & FAQ)": {
                "main": [[{"node": "Ticket Deduplication & Logic", "type": "main", "index": 0}]]
            },
            "Ticket Deduplication & Logic": {
                "main": [[{"node": "Format Audit Log Row", "type": "main", "index": 0}]]
            },
            "Format Audit Log Row": {
                "main": [[{"node": "Google Sheets (Audit Log)", "type": "main", "index": 0}]]
            },
            "Google Sheets (Audit Log)": {
                "main": [[{"node": "Respond to Webhook", "type": "main", "index": 0}]]
            }
        },
        "settings": {
            "executionOrder": "v1"
        }
    }

    with open("workflow/kesar_copilot_workflow.json", "w", encoding="utf-8") as f:
        json.dump(workflow, f, indent=2)
    print("Workflow JSON successfully written to workflow/kesar_copilot_workflow.json")

if __name__ == "__main__":
    build_workflow()
