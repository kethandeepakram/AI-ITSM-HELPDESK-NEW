import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import TicketForm from "../components/TicketForm";

export default function Dashboard({ onViewTicket, onNavigate }) {
  const [tickets, setTickets] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [provisioningRequests, setProvisioningRequests] = useState([]);
  const [activeTab, setActiveTab] = useState("tickets"); // "tickets", "audit", "software"
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Filters
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [priorityFilter, setPriorityFilter] = useState("All");

  const loadData = async () => {
    try {
      setLoading(true);
      setError("");

      const [ticketsRes, auditRes, provRes] = await Promise.all([
        api.getTickets().catch(() => ({ tickets: [] })),
        api.getAuditLogs().catch(() => ({ logs: [] })),
        api.getProvisioningRequests().catch(() => ({ requests: [] })),
      ]);

      setTickets(ticketsRes.tickets || []);
      setAuditLogs(auditRes.logs || []);
      setProvisioningRequests(provRes.requests || []);
    } catch (err) {
      setError(err.message || "Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 15000); // auto-refresh
    return () => clearInterval(interval);
  }, []);

  // Summary Metrics
  const totalTickets = tickets.length;
  const openTickets = tickets.filter((t) => t.status === "Open").length;
  const resolvedTickets = tickets.filter((t) => t.status === "Resolved").length;
  const escalatedTickets = tickets.filter((t) => t.status === "Escalated").length;
  const autoResolvedCount = tickets.filter((t) => t.automation_status === "Success").length;
  const softwareRequestsCount = provisioningRequests.length;

  const filteredTickets = tickets.filter((t) => {
    const q = searchTerm.toLowerCase();
    const matchesSearch =
      (t.ticket_id || "").toLowerCase().includes(q) ||
      (t.message || "").toLowerCase().includes(q) ||
      (t.category || "").toLowerCase().includes(q) ||
      (t.subcategory || "").toLowerCase().includes(q) ||
      (t.servicenow_incident || "").toLowerCase().includes(q);

    const matchesStatus = statusFilter === "All" || t.status === statusFilter;
    const matchesPriority = priorityFilter === "All" || t.priority === priorityFilter;

    return matchesSearch && matchesStatus && matchesPriority;
  });

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto", fontFamily: "system-ui, -apple-system, sans-serif" }}>
      {/* Title */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <div>
          <h1 style={{ fontSize: "28px", fontWeight: "800", color: "#0f172a", margin: "0 0 6px 0" }}>
            ITSM Operations & Automation Dashboard
          </h1>
          <p style={{ color: "#64748b", fontSize: "14px", margin: 0 }}>
            Live enterprise helpdesk analytics, self-healing status, ServiceNow incident synchronization, and audit trail.
          </p>
        </div>
        <button
          onClick={loadData}
          style={{
            padding: "8px 16px",
            backgroundColor: "#ffffff",
            border: "1px solid #cbd5e1",
            borderRadius: "8px",
            color: "#334155",
            fontWeight: "600",
            cursor: "pointer",
            fontSize: "13px",
          }}
        >
          🔄 Refresh
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "16px", marginBottom: "24px" }}>
        <div style={{ background: "#ffffff", padding: "18px", borderRadius: "12px", border: "1px solid #e2e8f0", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
          <div style={{ fontSize: "12px", fontWeight: "700", color: "#64748b", textTransform: "uppercase" }}>Total Tickets</div>
          <div style={{ fontSize: "28px", fontWeight: "800", color: "#0f172a", marginTop: "4px" }}>{totalTickets}</div>
          <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>All intake channels</div>
        </div>

        <div style={{ background: "#ffffff", padding: "18px", borderRadius: "12px", border: "1px solid #e2e8f0", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
          <div style={{ fontSize: "12px", fontWeight: "700", color: "#2563eb", textTransform: "uppercase" }}>Open Tickets</div>
          <div style={{ fontSize: "28px", fontWeight: "800", color: "#2563eb", marginTop: "4px" }}>{openTickets}</div>
          <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>Pending support action</div>
        </div>

        <div style={{ background: "#ffffff", padding: "18px", borderRadius: "12px", border: "1px solid #e2e8f0", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
          <div style={{ fontSize: "12px", fontWeight: "700", color: "#16a34a", textTransform: "uppercase" }}>AI-Resolved / Self-Healed</div>
          <div style={{ fontSize: "28px", fontWeight: "800", color: "#16a34a", marginTop: "4px" }}>{autoResolvedCount}</div>
          <div style={{ fontSize: "11px", color: "#16a34a", fontWeight: "600", marginTop: "4px" }}>
            {totalTickets > 0 ? `${Math.round((autoResolvedCount / totalTickets) * 100)}% Auto-Resolution` : "0%"}
          </div>
        </div>

        <div style={{ background: "#ffffff", padding: "18px", borderRadius: "12px", border: "1px solid #e2e8f0", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
          <div style={{ fontSize: "12px", fontWeight: "700", color: "#d97706", textTransform: "uppercase" }}>Escalated to Human</div>
          <div style={{ fontSize: "28px", fontWeight: "800", color: "#d97706", marginTop: "4px" }}>{escalatedTickets}</div>
          <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>Low confidence / out-of-scope</div>
        </div>

        <div style={{ background: "#ffffff", padding: "18px", borderRadius: "12px", border: "1px solid #e2e8f0", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
          <div style={{ fontSize: "12px", fontWeight: "700", color: "#7c3aed", textTransform: "uppercase" }}>Software Requests</div>
          <div style={{ fontSize: "28px", fontWeight: "800", color: "#7c3aed", marginTop: "4px" }}>{softwareRequestsCount}</div>
          <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>Automated provisioning</div>
        </div>

        <div style={{ background: "#ffffff", padding: "18px", borderRadius: "12px", border: "1px solid #e2e8f0", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
          <div style={{ fontSize: "12px", fontWeight: "700", color: "#0891b2", textTransform: "uppercase" }}>Audit Actions</div>
          <div style={{ fontSize: "28px", fontWeight: "800", color: "#0891b2", marginTop: "4px" }}>{auditLogs.length}</div>
          <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>Recorded automated tasks</div>
        </div>
      </div>

      {/* Ticket Creation Box */}
      <TicketForm onTicketCreated={() => loadData()} />

      {/* Tabs */}
      <div style={{ display: "flex", gap: "8px", borderBottom: "1px solid #e2e8f0", marginBottom: "16px" }}>
        <button
          onClick={() => setActiveTab("tickets")}
          style={{
            padding: "10px 18px",
            border: "none",
            background: "none",
            borderBottom: activeTab === "tickets" ? "3px solid #2563eb" : "3px solid transparent",
            color: activeTab === "tickets" ? "#2563eb" : "#64748b",
            fontWeight: "700",
            cursor: "pointer",
            fontSize: "14px",
          }}
        >
          🎫 All ITSM Tickets ({tickets.length})
        </button>

        <button
          onClick={() => setActiveTab("software")}
          style={{
            padding: "10px 18px",
            border: "none",
            background: "none",
            borderBottom: activeTab === "software" ? "3px solid #2563eb" : "3px solid transparent",
            color: activeTab === "software" ? "#2563eb" : "#64748b",
            fontWeight: "700",
            cursor: "pointer",
            fontSize: "14px",
          }}
        >
          💻 Software Provisioning ({provisioningRequests.length})
        </button>

        <button
          onClick={() => setActiveTab("audit")}
          style={{
            padding: "10px 18px",
            border: "none",
            background: "none",
            borderBottom: activeTab === "audit" ? "3px solid #2563eb" : "3px solid transparent",
            color: activeTab === "audit" ? "#2563eb" : "#64748b",
            fontWeight: "700",
            cursor: "pointer",
            fontSize: "14px",
          }}
        >
          🛡️ Automation Audit Trail ({auditLogs.length})
        </button>
      </div>

      {/* Tab 1: All Tickets */}
      {activeTab === "tickets" && (
        <div style={{ background: "#ffffff", borderRadius: "12px", border: "1px solid #e2e8f0", overflow: "hidden", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
          {/* Filters Bar */}
          <div style={{ padding: "16px 20px", borderBottom: "1px solid #e2e8f0", display: "flex", gap: "12px", flexWrap: "wrap", alignItems: "center" }}>
            <input
              type="text"
              placeholder="Search by ID, summary, category, ServiceNow..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                flex: 1,
                minWidth: "220px",
                padding: "8px 14px",
                borderRadius: "8px",
                border: "1px solid #cbd5e1",
                fontSize: "13px",
                outline: "none",
              }}
            />

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              style={{ padding: "8px 12px", borderRadius: "8px", border: "1px solid #cbd5e1", fontSize: "13px", background: "#ffffff" }}
            >
              <option value="All">All Statuses</option>
              <option value="Open">Open</option>
              <option value="Resolved">Resolved</option>
              <option value="Escalated">Escalated</option>
            </select>

            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              style={{ padding: "8px 12px", borderRadius: "8px", border: "1px solid #cbd5e1", fontSize: "13px", background: "#ffffff" }}
            >
              <option value="All">All Priorities</option>
              <option value="P1">P1 - Critical</option>
              <option value="P2">P2 - High</option>
              <option value="P3">P3 - Medium</option>
              <option value="P4">P4 - Low</option>
            </select>
          </div>

          {/* Tickets Table */}
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "13px" }}>
              <thead>
                <tr style={{ background: "#f8fafc", color: "#475569", borderBottom: "1px solid #e2e8f0" }}>
                  <th style={{ padding: "12px 16px" }}>Ticket ID</th>
                  <th style={{ padding: "12px 16px" }}>Issue Summary</th>
                  <th style={{ padding: "12px 16px" }}>Category</th>
                  <th style={{ padding: "12px 16px" }}>Priority</th>
                  <th style={{ padding: "12px 16px" }}>Status</th>
                  <th style={{ padding: "12px 16px" }}>ServiceNow Ref</th>
                  <th style={{ padding: "12px 16px" }}>Automation</th>
                  <th style={{ padding: "12px 16px" }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredTickets.length > 0 ? (
                  filteredTickets.map((t, idx) => (
                    <tr
                      key={idx}
                      style={{ borderBottom: "1px solid #f1f5f9", cursor: "pointer" }}
                      onClick={() => onViewTicket && onViewTicket(t)}
                      onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#f8fafc"}
                      onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "transparent"}
                    >
                      <td style={{ padding: "12px 16px", fontWeight: "700", color: "#1e293b" }}>
                        {t.ticket_id}
                      </td>
                      <td style={{ padding: "12px 16px", color: "#334155", maxWidth: "260px", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                        {t.summary || t.message}
                      </td>
                      <td style={{ padding: "12px 16px", color: "#64748b" }}>
                        {t.category} / {t.subcategory}
                      </td>
                      <td style={{ padding: "12px 16px" }}>
                        <span style={{
                          fontSize: "11px",
                          fontWeight: "700",
                          padding: "2px 8px",
                          borderRadius: "12px",
                          background: t.priority === "P1" ? "#fee2e2" : t.priority === "P2" ? "#ffedd5" : "#fef9c3",
                          color: t.priority === "P1" ? "#991b1b" : t.priority === "P2" ? "#9a3412" : "#854d0e",
                        }}>
                          {t.priority}
                        </span>
                      </td>
                      <td style={{ padding: "12px 16px" }}>
                        <span style={{
                          fontSize: "11px",
                          fontWeight: "700",
                          padding: "2px 8px",
                          borderRadius: "12px",
                          background: t.status === "Resolved" ? "#dcfce7" : t.status === "Escalated" ? "#fef3c7" : "#e0e7ff",
                          color: t.status === "Resolved" ? "#166534" : t.status === "Escalated" ? "#b45309" : "#3730a3",
                        }}>
                          {t.status}
                        </span>
                      </td>
                      <td style={{ padding: "12px 16px", color: "#0284c7", fontWeight: "600" }}>
                        {t.servicenow_incident || "Pending"}
                      </td>
                      <td style={{ padding: "12px 16px" }}>
                        {t.automation_status === "Success" ? (
                          <span style={{ color: "#16a34a", fontWeight: "600" }}>⚡ Auto-Resolved (Simulated)</span>
                        ) : t.automation_status === "Simulated" ? (
                          <span style={{ color: "#b45309", fontWeight: "600" }}>Demo Only (live incident left open)</span>
                        ) : t.automation_possible ? (
                          <span style={{ color: "#2563eb" }}>Eligible</span>
                        ) : (
                          <span style={{ color: "#94a3b8" }}>Manual</span>
                        )}
                      </td>
                      <td style={{ padding: "12px 16px" }}>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            if (onViewTicket) onViewTicket(t);
                          }}
                          style={{
                            padding: "4px 10px",
                            borderRadius: "6px",
                            border: "1px solid #cbd5e1",
                            background: "#ffffff",
                            cursor: "pointer",
                            fontSize: "12px",
                            fontWeight: "600",
                          }}
                        >
                          View →
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="8" style={{ padding: "32px", textAlign: "center", color: "#94a3b8" }}>
                      No tickets matching filter criteria.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: Software Provisioning */}
      {activeTab === "software" && (
        <div style={{ background: "#ffffff", borderRadius: "12px", border: "1px solid #e2e8f0", padding: "20px" }}>
          <h3 style={{ margin: "0 0 14px 0", fontSize: "16px", color: "#0f172a" }}>
            💻 Software Provisioning Requests (Scenario 4)
          </h3>
          {provisioningRequests.length > 0 ? (
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
              <thead>
                <tr style={{ background: "#f8fafc", textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>
                  <th style={{ padding: "10px" }}>Request ID</th>
                  <th style={{ padding: "10px" }}>Software Application</th>
                  <th style={{ padding: "10px" }}>Version</th>
                  <th style={{ padding: "10px" }}>Status</th>
                  <th style={{ padding: "10px" }}>ServiceNow Status</th>
                  <th style={{ padding: "10px" }}>Created At</th>
                </tr>
              </thead>
              <tbody>
                {provisioningRequests.map((r, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #f1f5f9" }}>
                    <td style={{ padding: "10px", fontWeight: "700", color: "#7c3aed" }}>{r.request_id}</td>
                    <td style={{ padding: "10px", fontWeight: "600" }}>{r.software || r.software_name}</td>
                    <td style={{ padding: "10px", color: "#64748b" }}>{r.version || r.approved_version || "Latest"}</td>
                    <td style={{ padding: "10px" }}>
                      <span style={{ background: "#f5f3ff", color: "#7c3aed", padding: "2px 8px", borderRadius: "10px", fontWeight: "700" }}>
                        {r.status}
                      </span>
                    </td>
                    <td style={{ padding: "10px", color: "#16a34a" }}>{r.servicenow_status || "Request created successfully"}</td>
                    <td style={{ padding: "10px", color: "#64748b" }}>{r.created_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div style={{ padding: "24px", textAlign: "center", color: "#94a3b8" }}>
              No software requests yet. Ask the chatbot: "I need Visual Studio Code installed on my laptop."
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Automation Audit Log */}
      {activeTab === "audit" && (
        <div style={{ background: "#ffffff", borderRadius: "12px", border: "1px solid #e2e8f0", padding: "20px" }}>
          <h3 style={{ margin: "0 0 14px 0", fontSize: "16px", color: "#0f172a" }}>
            🛡️ AI Automation Security Audit Trail
          </h3>
          {auditLogs.length > 0 ? (
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px" }}>
              <thead>
                <tr style={{ background: "#f8fafc", textAlign: "left", borderBottom: "1px solid #e2e8f0" }}>
                  <th style={{ padding: "10px" }}>Audit ID</th>
                  <th style={{ padding: "10px" }}>Timestamp</th>
                  <th style={{ padding: "10px" }}>Action</th>
                  <th style={{ padding: "10px" }}>Actor</th>
                  <th style={{ padding: "10px" }}>Target System</th>
                  <th style={{ padding: "10px" }}>Status</th>
                  <th style={{ padding: "10px" }}>Audit Details</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.map((a, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #f1f5f9" }}>
                    <td style={{ padding: "10px", fontFamily: "monospace", color: "#0284c7" }}>{a.audit_id}</td>
                    <td style={{ padding: "10px", color: "#64748b" }}>{a.timestamp}</td>
                    <td style={{ padding: "10px", fontWeight: "700" }}>{a.action}</td>
                    <td style={{ padding: "10px", color: "#334155" }}>{a.actor}</td>
                    <td style={{ padding: "10px", color: "#64748b" }}>{a.target}</td>
                    <td style={{ padding: "10px" }}>
                      <span style={{ background: "#dcfce7", color: "#166534", padding: "2px 6px", borderRadius: "8px", fontWeight: "700" }}>
                        {a.status}
                      </span>
                    </td>
                    <td style={{ padding: "10px", color: "#475569" }}>{a.details}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div style={{ padding: "24px", textAlign: "center", color: "#94a3b8" }}>
              No automated actions logged yet.
            </div>
          )}
        </div>
      )}
    </div>
  );
}