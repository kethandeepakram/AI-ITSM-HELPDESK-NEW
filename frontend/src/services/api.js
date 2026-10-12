import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000,
});

export const api = {
  // AI Chat & Decisioning
  sendChatMessage: async (message) => {
    const res = await client.post('/api/chat', { message });
    return res.data;
  },

  // Tickets
  getTickets: async () => {
    const res = await client.get('/api/tickets');
    return res.data;
  },

  createTicket: async (message) => {
    const res = await client.post('/api/tickets', { message });
    return res.data;
  },

  getTicketById: async (ticketId) => {
    const res = await client.get(`/api/tickets/${ticketId}`);
    return res.data;
  },

  resolveTicket: async (ticketId, reason = 'Resolved by user') => {
    const res = await client.post(`/api/tickets/${ticketId}/resolve`, { reason });
    return res.data;
  },

  escalateTicket: async (ticketId, reason = 'Escalated to human support') => {
    const res = await client.post(`/api/tickets/${ticketId}/escalate`, { reason });
    return res.data;
  },

  // Knowledge Base & RAG
  getKnowledgeArticles: async () => {
    const res = await client.get('/api/knowledge');
    return res.data;
  },

  searchKnowledge: async (query) => {
    const res = await client.post('/api/knowledge/search', { query });
    return res.data;
  },

  // Self-Healing & Provisioning
  executeAutomation: async (action, ticketId, softwareName = 'Visual Studio Code') => {
    const res = await client.post('/api/provisioning/execute', {
      action,
      ticket_id: ticketId,
      software_name: softwareName,
    });
    return res.data;
  },

  getProvisioningRequests: async () => {
    const res = await client.get('/api/provisioning/requests');
    return res.data;
  },

  // ServiceNow Integration
  getServiceNowIncidents: async () => {
    const res = await client.get('/api/servicenow/incidents');
    return res.data;
  },

  // Audit Logs
  getAuditLogs: async () => {
    const res = await client.get('/api/audit/logs');
    return res.data;
  },

  // Hackathon Demo Scenarios
  getDemoScenarios: async () => {
    const res = await client.get('/api/demo/scenarios');
    return res.data;
  },

  runDemoScenario: async (scenarioId) => {
    const res = await client.post(`/api/demo/run/${scenarioId}`);
    return res.data;
  },
};

export default api;
