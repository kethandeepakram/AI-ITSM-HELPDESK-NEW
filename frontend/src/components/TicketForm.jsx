import React, { useState } from 'react';
import { api } from '../services/api';

export default function TicketForm({ onTicketCreated }) {
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [createdResult, setCreatedResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim() || submitting) return;

    try {
      setSubmitting(true);
      setError('');
      setCreatedResult(null);

      const res = await api.createTicket(message.trim());
      if (res.success) {
        setCreatedResult(res);
        setMessage('');
        if (onTicketCreated) onTicketCreated(res.ticket);
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to submit ticket');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ background: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '20px', marginBottom: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
      <h3 style={{ margin: '0 0 12px 0', fontSize: '18px', color: '#0f172a' }}>
        ➕ Submit New IT Helpdesk Ticket
      </h3>
      <p style={{ margin: '0 0 16px 0', fontSize: '13px', color: '#64748b' }}>
        Type your IT issue. Our AI Agent will automatically classify the issue, calculate priority, assign the appropriate team, sync with ServiceNow, and trigger self-healing if eligible.
      </p>

      <form onSubmit={handleSubmit}>
        <textarea
          rows={3}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="e.g., I cannot connect to VPN since this morning. Authentication keeps failing."
          style={{
            width: '100%',
            boxSizing: 'border-box',
            padding: '12px',
            borderRadius: '8px',
            border: '1px solid #cbd5e1',
            fontSize: '14px',
            fontFamily: 'inherit',
            resize: 'vertical',
            outline: 'none',
          }}
        />

        {error && (
          <div style={{ marginTop: '8px', color: '#dc2626', fontSize: '13px' }}>
            ⚠️ {error}
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '12px' }}>
          <button
            type="submit"
            disabled={submitting || !message.trim()}
            style={{
              padding: '10px 20px',
              backgroundColor: submitting || !message.trim() ? '#94a3b8' : '#2563eb',
              color: '#ffffff',
              border: 'none',
              borderRadius: '8px',
              fontWeight: '600',
              cursor: submitting || !message.trim() ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              transition: 'background 0.2s',
            }}
          >
            {submitting ? 'Analyzing & Creating...' : 'Submit to AI Agent'}
          </button>
        </div>
      </form>

      {createdResult && (
        <div style={{ marginTop: '16px', padding: '14px', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px' }}>
          <div style={{ fontWeight: '700', color: '#166534', marginBottom: '6px' }}>
            ✅ Ticket Created: {createdResult.ticket.ticket_id} ({createdResult.ticket.status})
          </div>
          <div style={{ fontSize: '13px', color: '#15803d' }}>
            Category: <strong>{createdResult.ticket.category} / {createdResult.ticket.subcategory}</strong> | Priority: <strong>{createdResult.ticket.priority}</strong> | Assigned: <strong>{createdResult.ticket.assignment_group}</strong>
          </div>
          {createdResult.servicenow && (
            <div style={{ fontSize: '12px', color: '#166534', marginTop: '4px' }}>
              ServiceNow Reference: <strong>{createdResult.servicenow.incident_number}</strong> ({createdResult.servicenow.mode})
            </div>
          )}
        </div>
      )}
    </div>
  );
}
