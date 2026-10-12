import { useEffect, useState, useRef } from "react";
import { api } from "../services/api";

const quickActions = [
  { label: "🔑 Reset Password", value: "My password has expired." },
  { label: "🌐 VPN Connectivity", value: "I cannot connect to VPN since this morning. Authentication keeps failing." },
  { label: "📧 Outlook Sync", value: "How do I troubleshoot Outlook synchronization?" },
  { label: "💻 Install VS Code", value: "I need Visual Studio Code installed on my laptop." },
  { label: "📶 Office Wi-Fi", value: "My laptop cannot connect to the corporate Wi-Fi." },
];

export default function Chatbot() {
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "👋 Hello! I am your AI IT Helpdesk Assistant. Ask me any IT issue, request software, or choose a quick action below.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSendMessage = async (customMessage) => {
    const message = (customMessage || input).trim();
    if (!message || loading) return;

    // Add user message
    const userMsg = {
      sender: "user",
      text: message,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      // 1. Answer the employee's question using AI + RAG.
      // Creating a ticket is an explicit follow-up action, not automatic for every question.
      const chatData = await api.sendChatMessage(message);

      const botMsg = {
        sender: "bot",
        text: chatData.ai_response,
        chatData: chatData,
        originalMessage: message,
        ticket: null,
        ticketCreating: false,
        ticketError: null,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: `⚠️ Request Error: ${err.message || "Failed to communicate with helpdesk backend"}.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTicket = async (messageIndex, originalMessage) => {
    if (!originalMessage) return;

    setMessages((prev) => prev.map((message, index) =>
      index === messageIndex
        ? { ...message, ticketCreating: true, ticketError: null }
        : message
    ));

    try {
      const ticketResponse = await api.createTicket(originalMessage);
      setMessages((prev) => prev.map((message, index) =>
        index === messageIndex
          ? { ...message, ticket: ticketResponse.ticket, ticketCreating: false, ticketError: null }
          : message
      ));
    } catch (err) {
      setMessages((prev) => prev.map((message, index) =>
        index === messageIndex
          ? {
              ...message,
              ticketCreating: false,
              ticketError: err.message || "Could not create the ticket. Please try again.",
            }
          : message
      ));
    }
  };

  return (
    <div style={{
      background: "#ffffff",
      borderRadius: "16px",
      border: "1px solid #e2e8f0",
      boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.08)",
      display: "flex",
      flexDirection: "column",
      height: "calc(100vh - 120px)",
      maxHeight: "800px",
      overflow: "hidden",
    }}>
      {/* Header */}
      <div style={{
        background: "#0f172a",
        color: "#ffffff",
        padding: "16px 20px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div style={{
            width: "10px",
            height: "10px",
            borderRadius: "50%",
            backgroundColor: "#22c55e",
            boxShadow: "0 0 8px #22c55e",
          }} />
          <div>
            <div style={{ fontWeight: "700", fontSize: "14px" }}>IT Support AI Agent</div>
            <div style={{ fontSize: "11px", color: "#94a3b8" }}>RAG + Self-Healing Active</div>
          </div>
        </div>
        <span style={{ fontSize: "11px", background: "#1e293b", color: "#38bdf8", padding: "3px 8px", borderRadius: "12px", fontWeight: "600" }}>
          ServiceNow Integration
        </span>
      </div>

      {/* Messages Scroll Area */}
      <div style={{
        flex: 1,
        overflowY: "auto",
        padding: "16px",
        display: "flex",
        flexDirection: "column",
        gap: "14px",
        backgroundColor: "#f8fafc",
      }}>
        {messages.map((m, idx) => {
          const isBot = m.sender === "bot";
          return (
            <div
              key={idx}
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: isBot ? "flex-start" : "flex-end",
              }}
            >
              <div
                style={{
                  maxWidth: "92%",
                  padding: "12px 16px",
                  borderRadius: isBot ? "14px 14px 14px 2px" : "14px 14px 2px 14px",
                  backgroundColor: isBot ? "#ffffff" : "#2563eb",
                  color: isBot ? "#1e293b" : "#ffffff",
                  fontSize: "13px",
                  lineHeight: "1.5",
                  boxShadow: "0 1px 3px rgba(0,0,0,0.06)",
                  border: isBot ? "1px solid #e2e8f0" : "none",
                  whiteSpace: "pre-line",
                }}
              >
                {m.text}

                {isBot && m.chatData && !m.ticket && (
                  <div style={{ marginTop: "10px", display: "flex", flexDirection: "column", gap: "6px" }}>
                    <button
                      onClick={() => handleCreateTicket(idx, m.originalMessage)}
                      disabled={m.ticketCreating}
                      style={{
                        padding: "7px 11px",
                        borderRadius: "7px",
                        border: "1px solid #2563eb",
                        background: m.ticketCreating ? "#dbeafe" : "#eff6ff",
                        color: "#1d4ed8",
                        fontSize: "11px",
                        fontWeight: "700",
                        cursor: m.ticketCreating ? "wait" : "pointer",
                      }}
                    >
                      {m.ticketCreating ? "Creating ticket..." : "🎫 Create Ticket / ServiceNow Incident"}
                    </button>
                    {m.ticketError && (
                      <span role="alert" style={{ color: "#b91c1c", fontSize: "11px" }}>
                        {m.ticketError}
                      </span>
                    )}
                  </div>
                )}

                {/* Structured Ticket & Action Card */}
                {isBot && m.ticket && (
                  <div style={{
                    marginTop: "10px",
                    paddingTop: "10px",
                    borderTop: "1px solid #e2e8f0",
                    fontSize: "11px",
                    color: "#475569",
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                      <strong>🎫 Ticket: {m.ticket.ticket_id}</strong>
                      <span style={{
                        padding: "1px 6px",
                        borderRadius: "8px",
                        fontWeight: "700",
                        background: m.ticket.status === "Resolved" ? "#dcfce7" : "#e0e7ff",
                        color: m.ticket.status === "Resolved" ? "#166534" : "#3730a3",
                      }}>
                        {m.ticket.status}
                      </span>
                    </div>

                    <div>Category: <strong>{m.ticket.category} / {m.ticket.subcategory}</strong></div>
                    <div>Priority: <strong>{m.ticket.priority}</strong> | Group: <strong>{m.ticket.assignment_group}</strong></div>

                    {m.ticket.servicenow_incident && (
                      <div style={{ marginTop: "4px", color: "#0369a1", fontWeight: "600" }}>
                        🔗 ServiceNow: {m.ticket.servicenow_incident} ({m.ticket.servicenow_status || "Created"})
                      </div>
                    )}

                    {m.ticket.automation_status && (
                      <div style={{ marginTop: "4px", color: "#166534", fontWeight: "700" }}>
                        ⚡ Simulated Self-Healing: {m.ticket.automation_action || "Automation"} workflow completed (demo only)
                      </div>
                    )}
                  </div>
                )}
              </div>
              <span style={{ fontSize: "10px", color: "#94a3b8", marginTop: "4px", marginInline: "4px" }}>
                {m.timestamp}
              </span>
            </div>
          );
        })}

        {loading && (
          <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#64748b", fontSize: "12px" }}>
            <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#3b82f6" }} />
            AI Agent is analyzing the request and searching approved knowledge...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Action Suggestions */}
      <div style={{
        padding: "10px 14px",
        background: "#ffffff",
        borderTop: "1px solid #e2e8f0",
        display: "flex",
        gap: "6px",
        overflowX: "auto",
        whiteSpace: "nowrap",
      }}>
        {quickActions.map((qa, i) => (
          <button
            key={i}
            onClick={() => handleSendMessage(qa.value)}
            disabled={loading}
            style={{
              padding: "5px 10px",
              borderRadius: "14px",
              border: "1px solid #cbd5e1",
              background: "#f8fafc",
              color: "#334155",
              fontSize: "11px",
              cursor: "pointer",
              fontWeight: "600",
              flexShrink: 0,
            }}
          >
            {qa.label}
          </button>
        ))}
      </div>

      {/* Input Field */}
      <div style={{
        padding: "14px 16px",
        background: "#ffffff",
        borderTop: "1px solid #e2e8f0",
        display: "flex",
        gap: "8px",
      }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
          placeholder="Ask IT question or report issue..."
          disabled={loading}
          style={{
            flex: 1,
            padding: "10px 14px",
            borderRadius: "8px",
            border: "1px solid #cbd5e1",
            fontSize: "13px",
            outline: "none",
          }}
        />
        <button
          onClick={() => handleSendMessage()}
          disabled={loading || !input.trim()}
          style={{
            padding: "10px 16px",
            backgroundColor: loading || !input.trim() ? "#94a3b8" : "#2563eb",
            color: "#ffffff",
            border: "none",
            borderRadius: "8px",
            fontWeight: "700",
            cursor: loading || !input.trim() ? "not-allowed" : "pointer",
            fontSize: "13px",
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}
