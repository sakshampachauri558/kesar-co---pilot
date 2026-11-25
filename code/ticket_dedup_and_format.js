/**
 * ticket_dedup_and_format.js
 * Handles support ticketing logic:
 * 1. Checks if ticket is required (complaints, returns/refunds)
 * 2. Deduplicates tickets by searching existing open tickets for order_id
 * 3. Formats create or update payload
 */
const item = $input.first().json;
const intent = item.classification?.intent;
const orderId = item.order?.order_id || item.classification?.order_id || null;
const emailId = item.email?.email_id || item.email_id;
const customerEmail = item.order?.customer_email || item.email?.from_email || '';
const summary = item.classification?.summary || '';
const sentiment = item.classification?.sentiment || 'neutral';
const existingTickets = item.existing_tickets || [];

const ticketRequired = (intent === 'return_refund' || intent === 'complaint');

if (!ticketRequired) {
  return {
    json: {
      ...item,
      ticket_action: 'NONE',
      ticket_id: null
    }
  };
}

// Set Priority
let priority = 'Medium';
if (intent === 'complaint' || sentiment === 'angry') {
  priority = 'High';
} else if (intent === 'return_refund') {
  priority = 'Medium';
}

// Deduplication check: Look for an open ticket with the same order_id
let existingOpenTicket = null;
if (orderId) {
  existingOpenTicket = existingTickets.find(t => 
    (t.order_id || '').toUpperCase() === orderId.toUpperCase() && 
    (t.status || '').toLowerCase() !== 'closed'
  );
}

const timestamp = new Date().toISOString();

if (existingOpenTicket) {
  // Update existing ticket
  const existingEmailIds = (existingOpenTicket.email_ids || '').split(',').map(s => s.trim()).filter(Boolean);
  if (!existingEmailIds.includes(emailId)) {
    existingEmailIds.push(emailId);
  }
  const updatedNotes = `${existingOpenTicket.notes || ''} | [${emailId}]: ${summary}`.trim();

  return {
    json: {
      ...item,
      ticket_action: 'UPDATE',
      ticket_id: existingOpenTicket.ticket_id,
      ticket_data: {
        ticket_id: existingOpenTicket.ticket_id,
        updated_at: timestamp,
        email_ids: existingEmailIds.join(', '),
        notes: updatedNotes
      }
    }
  };
} else {
  // Create new ticket
  const nextNumber = (existingTickets.length + 1).toString().padStart(3, '0');
  const newTicketId = `TKT-${nextNumber}`;

  return {
    json: {
      ...item,
      ticket_action: 'CREATE',
      ticket_id: newTicketId,
      ticket_data: {
        ticket_id: newTicketId,
        created_at: timestamp,
        updated_at: timestamp,
        order_id: orderId || 'N/A',
        customer_email: customerEmail,
        email_ids: emailId,
        intent: intent,
        priority: priority,
        status: 'Open',
        summary: summary,
        notes: `Created from ${emailId}: ${summary}`
      }
    }
  };
}
