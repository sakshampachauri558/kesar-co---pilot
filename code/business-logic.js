/**
 * business-logic.js
 * Core deterministic business logic for Kesar & Co. AI Support Copilot:
 * 1. Security: Prompt injection detection
 * 2. Privacy: Sender email vs Order customer_email verification
 * 3. Date Arithmetic: 7-day return & 48h damaged policy relative to 2026-11-20
 * 4. Ticketing: Deduplication and priority assignment
 */

function processBusinessLogic({ email, classification, orders, existingTickets }) {
  const fromEmail = (email.from_email || email.from?.email || '').trim().toLowerCase();
  const body = email.body || '';
  const orderId = classification.order_id || null;
  const intent = classification.intent || 'other';
  const sentiment = classification.sentiment || 'neutral';
  const summary = classification.summary || '';

  // 1. Prompt Injection Defense
  const injectionRegex = /(ignore all previous instructions|system note|override policy|mark.*approved|vip customer)/i;
  const promptInjectionDetected = injectionRegex.test(body);

  // 2. Order Lookup
  let matchedOrder = null;
  if (orderId) {
    matchedOrder = orders.find(o => o.order_id.toUpperCase() === orderId.toUpperCase());
  }
  if (!matchedOrder && fromEmail) {
    matchedOrder = orders.find(o => o.customer_email.toLowerCase().trim() === fromEmail);
  }

  const orderFound = !!matchedOrder;
  let privacyViolation = false;
  let orderDetailsAllowed = false;

  // 3. Privacy Verification
  if (matchedOrder) {
    if (matchedOrder.customer_email.toLowerCase().trim() !== fromEmail) {
      privacyViolation = true;
      orderDetailsAllowed = false;
    } else {
      orderDetailsAllowed = true;
    }
  }

  // 4. Deterministic Date Arithmetic (Scenario Date: 2026-11-20)
  const SCENARIO_DATE = new Date('2026-11-20T00:00:00+05:30');
  let daysSinceDelivery = null;
  let returnEligible = false;
  let damagedWithin48h = false;

  if (matchedOrder && matchedOrder.delivered_date) {
    const deliveryDate = new Date(matchedOrder.delivered_date + 'T00:00:00+05:30');
    daysSinceDelivery = Math.floor((SCENARIO_DATE - deliveryDate) / (1000 * 60 * 60 * 24));
    returnEligible = (daysSinceDelivery <= 7 && daysSinceDelivery >= 0);
    damagedWithin48h = (daysSinceDelivery <= 2 && daysSinceDelivery >= 0);
  }

  // 5. Ticketing & Deduplication
  let ticketAction = 'NONE';
  let ticketId = '';
  let priority = 'Medium';

  if (intent === 'return_refund' || intent === 'complaint') {
    priority = (intent === 'complaint' || sentiment === 'angry') ? 'High' : 'Medium';
    const targetOrderId = matchedOrder?.order_id || orderId;

    const existingOpenTicket = (existingTickets || []).find(t => 
      t.order_id && targetOrderId && t.order_id.toUpperCase() === targetOrderId.toUpperCase() &&
      (t.status || '').toLowerCase() !== 'closed'
    );

    if (existingOpenTicket) {
      ticketAction = 'UPDATE';
      ticketId = existingOpenTicket.ticket_id;
    } else {
      ticketAction = 'CREATE';
      ticketId = `TKT-${String((existingTickets || []).length + 1).padStart(3, '0')}`;
    }
  }

  // 6. Human Escalation (needs_human)
  let needsHuman = false;
  const reasons = [];

  if (promptInjectionDetected) {
    needsHuman = true;
    reasons.push('Prompt injection detected');
  }
  if (privacyViolation) {
    needsHuman = true;
    reasons.push('Privacy violation: sender email does not match order record');
  }
  if (/eczema|cure/i.test(body)) {
    needsHuman = true;
    reasons.push('Medical claim inquiry');
  }
  if (classification.confidence < 0.70) {
    needsHuman = true;
    reasons.push('Low classification confidence');
  }

  return {
    order_found: orderFound,
    privacy_violation: privacyViolation,
    order_details_allowed: orderDetailsAllowed,
    days_since_delivery: daysSinceDelivery,
    return_eligible: returnEligible,
    damaged_within_48h: damagedWithin48h,
    ticket_action: ticketAction,
    ticket_id: ticketId,
    ticket_priority: priority,
    needs_human: needsHuman,
    escalation_reasons: reasons
  };
}

module.exports = { processBusinessLogic };
