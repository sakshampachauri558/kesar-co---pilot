/**
 * order_lookup_and_rules.js
 * Performs deterministic business logic:
 * 1. Order lookup by order_id, falling back to from_email
 * 2. Strict Privacy check (email matching)
 * 3. Deterministic date arithmetic relative to scenario reference date (2026-11-20)
 * 4. Return & damaged policy verification
 */
const item = $input.first().json;
const email = item.email || {};
const classification = item.classification || {};
const orders = item.orders_database || [];

const emailId = email.email_id || item.email_id;
const fromEmail = (email.from_email || item.from_email || '').toLowerCase().trim();
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

// 3. Deterministic Date Arithmetic (Scenario Date: 2026-11-20)
const SCENARIO_DATE = new Date('2026-11-20T00:00:00+05:30');
let daysSinceDelivery = null;
let returnEligible = false;
let damagedWindowValid = false;

if (matchedOrder && matchedOrder.delivered_date) {
  const deliveryDate = new Date(matchedOrder.delivered_date + 'T00:00:00+05:30');
  const diffMs = SCENARIO_DATE.getTime() - deliveryDate.getTime();
  daysSinceDelivery = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  // Return window: 7 days
  returnEligible = (daysSinceDelivery <= 7 && daysSinceDelivery >= 0);
  // Damaged / missing reporting window: 48 hours (~2 days)
  damagedWindowValid = (daysSinceDelivery <= 2 && daysSinceDelivery >= 0);
}

// 4. Escalation Flags
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

if (classification.confidence < 0.70) {
  needsHuman = true;
  reasons.push(`Low classification confidence (${classification.confidence})`);
}

if (classification.intent === 'other' && !['SEO Rankers', 'Simran Kaur'].some(s => (email.from_name || '').includes(s))) {
  // Partnership, medical or unknown
  needsHuman = true;
  reasons.push('Unclassified or partnership enquiry');
}

return {
  json: {
    ...item,
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
};
