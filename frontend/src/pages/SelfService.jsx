import React, { useState } from "react";
import { api } from "../services/api";

export default function SelfService({ onNavigate }) {
  const [executingAction, setExecutingAction] = useState(null);
  const [actionResult, setActionResult] = useState(null);

  const services = [
    {
      title: "Self-Service Password Reset",
      description: "Instantly reset expired Active Directory passwords via automated biometric/SMS challenge.",
      icon: "🔐",
      action: "password_reset",
      category: "Account & Access",
      prompt: "My password has expired.",
    },
    {
      title: "Account Lockout Resolution",
      description: "Detect and release account lockouts caused by repeated failed login attempts.",
      icon: "🔓",
      action: "account_unlock",
      category: "Account & Access",
      prompt: "My account is locked out.",
    },
    {
      title: "VPN Diagnostic & Self-Heal",
      description: "Verify tunnel health to vpn.company.internal, flush DNS, and cycle virtual network adapters.",
      icon: "🌐",
      action: "vpn_status_check",
      category: "Network",
      prompt: "I cannot connect to VPN since this morning. Authentication keeps failing.",
    },
    {
      title: "Software Catalog Provisioning",
      description: "Request enterprise tools like Visual Studio Code, Docker Desktop, or Postman with instant approval.",
      icon: "💻",
      action: "software_install",
      category: "Software",
      prompt: "I need Visual Studio Code installed on my laptop.",
    },
    {
      title: "Local Cache Purge & Rebuild",
      description: "Rebuild Outlook OST sync caches and purge temporary roaming profile app data.",
      icon: "🧹",
      action: "cache_clear",
      category: "Software",
      prompt: "Clear application cache and repair synchronization.",
    },
    {
      title: "Wi-Fi & Service Restarter",
      description: "Restart WLAN AutoConfig and Network Location Awareness services on your workstation.",
      icon: "📶",
      action: "service_restart",
      category: "Network",
      prompt: "Restart wireless network adapter and services.",
    },
  ];

  const handleExecute = async (service) => {
    try {
      setExecutingAction(service.action);
      setActionResult(null);

      // Create ticket first
      const ticketRes = await api.createTicket(service.prompt);
      const ticket = ticketRes.ticket;

      // Ticket creation already executes the classifier-approved action when
      // eligible. Reuse that result rather than running the same action twice.
      let autoRes = ticket?.automation_result;
      const alreadyExecuted =
        ticket?.automation_status === "Success" &&
        autoRes &&
        autoRes.success === true;

      if (!alreadyExecuted) {
        autoRes = await api.executeAutomation(
          service.action,
          ticket.ticket_id,
          "Visual Studio Code"
        );
      }

      setActionResult({
        service: service.title,
        ticket,
        automation: autoRes,
      });
    } catch (err) {
      alert(`Action failed: ${err.message}`);
    } finally {
      setExecutingAction(null);
    }
  };

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto", fontFamily: "system-ui, -apple-system, sans-serif" }}>
      {/* Header */}
      <div style={{ marginBottom: "28px" }}>
        <h1 style={{ fontSize: "28px", fontWeight: "800", color: "#0f172a", margin: "0 0 8px 0" }}>
          🙋 Employee IT Self-Service Portal
        </h1>
        <p style={{ color: "#64748b", fontSize: "15px", margin: 0 }}>
          Resolve common workstation and access problems without waiting in an IT support queue. Actions trigger intelligent automation and log a full audit trail.
        </p>
      </div>

      {/* Result Notification Card */}
      {actionResult && (
        <div style={{
          background: "#f0fdf4",
          border: "1px solid #bbf7d0",
          borderRadius: "12px",
          padding: "20px",
          marginBottom: "24px",
          boxShadow: "0 2px 4px rgba(0,0,0,0.05)",
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <h3 style={{ margin: 0, fontSize: "17px", color: "#166534" }}>
              ⚡ Automated Self-Healing Completed: {actionResult.service}
            </h3>
            <button
              onClick={() => setActionResult(null)}
              style={{ background: "none", border: "none", cursor: "pointer", color: "#15803d", fontWeight: "700" }}
            >
              ✕
            </button>
          </div>

          <div style={{ fontSize: "13px", color: "#15803d", lineHeight: "1.6" }}>
            <div>Ticket ID: <strong>{actionResult.ticket.ticket_id}</strong> (Status: <strong>{actionResult.ticket.status}</strong>)</div>
            <div>ServiceNow Incident: <strong>{actionResult.ticket.servicenow_incident}</strong></div>
            <div>Action Message: <strong>{actionResult.automation.message}</strong></div>
          </div>

          {actionResult.automation.steps_executed && (
            <div style={{ marginTop: "12px", background: "#ffffff", padding: "10px 14px", borderRadius: "8px", border: "1px solid #dcfce7" }}>
              <div style={{ fontSize: "11px", fontWeight: "700", color: "#15803d", marginBottom: "4px" }}>WORKFLOW STEPS VERIFIED:</div>
              {actionResult.automation.steps_executed.map((st, i) => (
                <div key={i} style={{ fontSize: "12px", color: "#166534" }}>{st}</div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Services Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "20px" }}>
        {services.map((service, idx) => (
          <div
            key={idx}
            style={{
              backgroundColor: "#ffffff",
              border: "1px solid #e2e8f0",
              borderRadius: "14px",
              padding: "24px",
              boxShadow: "0 2px 4px rgba(0,0,0,0.04)",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
            }}
          >
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                <span style={{ fontSize: "32px" }}>{service.icon}</span>
                <span style={{ fontSize: "11px", background: "#f1f5f9", color: "#475569", padding: "2px 8px", borderRadius: "10px", fontWeight: "600" }}>
                  {service.category}
                </span>
              </div>

              <h3 style={{ margin: "0 0 8px 0", fontSize: "18px", color: "#0f172a" }}>
                {service.title}
              </h3>

              <p style={{ color: "#64748b", fontSize: "13px", lineHeight: "1.5", margin: "0 0 20px 0" }}>
                {service.description}
              </p>
            </div>

            <div style={{ display: "flex", gap: "8px" }}>
              <button
                onClick={() => handleExecute(service)}
                disabled={executingAction !== null}
                style={{
                  flex: 1,
                  padding: "10px 16px",
                  border: "none",
                  borderRadius: "8px",
                  cursor: executingAction !== null ? "not-allowed" : "pointer",
                  backgroundColor: executingAction === service.action ? "#3b82f6" : "#0f172a",
                  color: "#ffffff",
                  fontSize: "13px",
                  fontWeight: "700",
                  transition: "background 0.2s",
                }}
              >
                {executingAction === service.action ? "Running..." : "⚡ Run Self-Heal"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}