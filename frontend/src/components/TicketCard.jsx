import React from 'react';

export default function TicketCard({ ticket, onViewTicket }) {
  if (!ticket) return null;

  const getPriorityBadge = (priority) => {
    switch (priority) {
      case 'P1': return { bg: '#fee2e2', text: '#991b1b', border: '#f87171' };
      case 'P2': return { bg: '#ffedd5', text: '#9a3412', border: '#fb923c' };
      case 'P3': return { bg: '#fef9c3', text: '#854d0e', border: '#facc15' };
      default: return { bg: '#f1f5f9', text: '#475569', border: '#cbd5e1' };
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Resolved': return { bg: '#dcfce7', text: '#166534' };
      case 'Escalated': return { bg: '#fef3c7', text: '#b45309' };
      default: return { bg: '#e0e7ff', text: '#3730a3' };
    }
  };

  const pStyle = getPriorityBadge(ticket.priority);
  const sStyle = getStatusBadge(ticket.status);

  return (
    <div
      style={{
        background: '#ffffff',
        border: '1px solid #e2e8f0',
        borderRadius: '10px',
        padding: '16px',
        marginBottom: '12px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
        cursor: 'pointer',
        transition: 'transform 0.15s, box-shadow 0.15s',
      }}
      onClick={() => onViewTicket && onViewTicket(ticket)}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.05)';
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontWeight: '700', fontSize: '14px', color: '#1e293b' }}>
            {ticket.ticket_id || ticket.id}
          </span>
          {ticket.servicenow_incident && (
            <span style={{ fontSize: '11px', background: '#f1f5f9', color: '#0f172a', padding: '2px 6px', borderRadius: '4px', fontWeight: '600' }}>
              SNOW: {ticket.servicenow_incident}
            </span>
          )}
        </div>
        <div style={{ display: 'flex', gap: '6px' }}>
          <span style={{
            fontSize: '11px',
            fontWeight: '700',
            padding: '2px 8px',
            borderRadius: '12px',
            backgroundColor: pStyle.bg,
            color: pStyle.text,
            border: `1px solid ${pStyle.border}`
          }}>
            {ticket.priority || 'P3'}
          </span>
          <span style={{
            fontSize: '11px',
            fontWeight: '700',
            padding: '2px 8px',
            borderRadius: '12px',
            backgroundColor: sStyle.bg,
            color: sStyle.text,
          }}>
            {ticket.status || 'Open'}
          </span>
        </div>
      </div>

      <div style={{ fontSize: '14px', color: '#334155', fontWeight: '500', marginBottom: '10px' }}>
        {ticket.summary || ticket.message || ticket.title}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12px', color: '#64748b' }}>
        <div>
          <span>📂 {ticket.category}</span>
          {ticket.subcategory && <span> / {ticket.subcategory}</span>}
        </div>
        <div>
          <span>👥 {ticket.assignment_group || 'IT Support'}</span>
        </div>
      </div>
    </div>
  );
}
