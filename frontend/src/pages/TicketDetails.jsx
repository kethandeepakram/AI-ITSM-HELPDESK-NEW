import React from "react";

function TicketDetails({ ticket, onBack }) {
  if (!ticket) {
    return (
      <div
        style={{
          padding: "40px",
          fontFamily: "Arial, sans-serif",
          maxWidth: "1000px",
          margin: "0 auto",
        }}
      >
        <h1>Ticket Details</h1>
        <p>No ticket selected.</p>

        <button
          onClick={onBack}
          style={{
            padding: "10px 18px",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
            backgroundColor: "#1f2937",
            color: "white",
          }}
        >
          ← Back to Dashboard
        </button>
      </div>
    );
  }

  const isResolved = ticket.status === "Resolved";
  const isAutomated = ticket.automation_status === "Success";

  return (
    <div
      style={{
        padding: "35px",
        fontFamily: "Arial, sans-serif",
        maxWidth: "1100px",
        margin: "0 auto",
        backgroundColor: "#f8fafc",
        minHeight: "100vh",
      }}
    >
      {/* Back Button */}
      <button
        onClick={onBack}
        style={{
          padding: "10px 18px",
          marginBottom: "25px",
          border: "none",
          borderRadius: "8px",
          cursor: "pointer",
          backgroundColor: "#1f2937",
          color: "white",
          fontSize: "14px",
        }}
      >
        ← Back to Dashboard
      </button>

      {/* Page Header */}
      <div style={{ marginBottom: "25px" }}>
        <h1 style={{ marginBottom: "8px" }}>Ticket Details</h1>

        <p style={{ color: "#64748b", margin: 0 }}>
          AI-powered ITSM ticket information and classification
        </p>
      </div>

      {/* Main Ticket Header */}
      <div
        style={{
          backgroundColor: "white",
          border: "1px solid #e2e8f0",
          borderRadius: "12px",
          padding: "28px",
          boxShadow: "0 3px 10px rgba(0,0,0,0.05)",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            gap: "20px",
          }}
        >
          <div style={{ flex: 1 }}>
            <p
              style={{
                margin: "0 0 8px",
                color: "#64748b",
                fontSize: "14px",
              }}
            >
              Ticket ID
            </p>

            <h2
              style={{
                margin: "0 0 15px",
                color: "#111827",
              }}
            >
              {ticket.ticket_id || ticket.id}
            </h2>

            <h3 style={{ margin: 0 }}>
              {ticket.title || ticket.message}
            </h3>
          </div>

          {/* Status */}
          <div style={{ textAlign: "right" }}>
            <span
              style={{
                display: "inline-block",
                padding: "7px 14px",
                borderRadius: "20px",
                backgroundColor: isResolved
                  ? "#dcfce7"
                  : "#fef3c7",
                color: isResolved
                  ? "#166534"
                  : "#92400e",
                fontWeight: "bold",
              }}
            >
              {ticket.status}
            </span>

            <div style={{ marginTop: "10px" }}>
              <span
                style={{
                  display: "inline-block",
                  padding: "6px 12px",
                  borderRadius: "20px",
                  backgroundColor:
                    ticket.priority === "P1" ||
                    ticket.priority === "P2"
                      ? "#fee2e2"
                      : "#e0f2fe",
                  color:
                    ticket.priority === "P1" ||
                    ticket.priority === "P2"
                      ? "#991b1b"
                      : "#075985",
                  fontWeight: "bold",
                }}
              >
                {ticket.priority}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* AI Classification */}
      <div
        style={{
          backgroundColor: "white",
          border: "1px solid #e2e8f0",
          borderRadius: "12px",
          padding: "28px",
          marginTop: "20px",
          boxShadow: "0 3px 10px rgba(0,0,0,0.05)",
        }}
      >
        <h2 style={{ marginTop: 0 }}>🤖 AI Classification</h2>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(2, 1fr)",
            gap: "18px",
          }}
        >
          <InfoItem
            label="Intent"
            value={ticket.intent}
          />

          <InfoItem
            label="Category"
            value={ticket.category}
          />

          <InfoItem
            label="Subcategory"
            value={ticket.subcategory}
          />

          <InfoItem
            label="Urgency"
            value={ticket.urgency}
          />

          <InfoItem
            label="Assignment Group"
            value={ticket.assignment_group}
          />

          <InfoItem
            label="Priority"
            value={ticket.priority}
          />
        </div>
      </div>

      {/* Issue Details */}
      <div
        style={{
          backgroundColor: "white",
          border: "1px solid #e2e8f0",
          borderRadius: "12px",
          padding: "28px",
          marginTop: "20px",
          boxShadow: "0 3px 10px rgba(0,0,0,0.05)",
        }}
      >
        <h2 style={{ marginTop: 0 }}>📝 Issue Details</h2>

        <div
          style={{
            padding: "18px",
            backgroundColor: "#f8fafc",
            borderRadius: "10px",
            marginBottom: "20px",
          }}
        >
          <strong>User Message</strong>

          <p
            style={{
              marginBottom: 0,
              lineHeight: "1.6",
            }}
          >
            {ticket.message || ticket.title}
          </p>
        </div>

        <div
          style={{
            padding: "18px",
            backgroundColor: "#f8fafc",
            borderRadius: "10px",
          }}
        >
          <strong>💡 Suggested Action</strong>

          <p
            style={{
              marginBottom: 0,
              lineHeight: "1.6",
            }}
          >
            {ticket.suggested_action || "No suggested action available."}
          </p>
        </div>
      </div>

      {/* Self-Healing Automation */}
      <div
        style={{
          backgroundColor: "white",
          border: "1px solid #e2e8f0",
          borderRadius: "12px",
          padding: "28px",
          marginTop: "20px",
          boxShadow: "0 3px 10px rgba(0,0,0,0.05)",
        }}
      >
        <h2 style={{ marginTop: 0 }}>
          🤖 Self-Healing Automation
        </h2>

        <div
          style={{
            padding: "18px",
            borderRadius: "10px",
            backgroundColor: isAutomated
              ? "#f0fdf4"
              : "#f8fafc",
          }}
        >
          <p>
            <strong>Automation Possible:</strong>{" "}
            {ticket.automation_possible ? "Yes" : "No"}
          </p>

          <p>
            <strong>Automation Status:</strong>{" "}
            {ticket.automation_status || "Not Executed"}
          </p>

          <p>
            <strong>Execution Mode:</strong>{" "}
            {ticket.automation_result?.mode || (ticket.automation_status ? "SIMULATED (legacy record)" : "Not executed")}
          </p>

          <p>
            <strong>Automation Action:</strong>{" "}
            {ticket.automation_action || "None"}
          </p>

          {isAutomated && (
            <div
              style={{
                marginTop: "15px",
                padding: "10px 14px",
                borderRadius: "8px",
                backgroundColor: "#dcfce7",
                color: "#166534",
                fontWeight: "bold",
              }}
            >
              ✅ Simulated workflow completed; no real endpoint or directory change was made.
            </div>
          )}
        </div>
      </div>

      {/* Timeline */}
      <div
        style={{
          backgroundColor: "white",
          border: "1px solid #e2e8f0",
          borderRadius: "12px",
          padding: "28px",
          marginTop: "20px",
          boxShadow: "0 3px 10px rgba(0,0,0,0.05)",
        }}
      >
        <h2 style={{ marginTop: 0 }}>🕒 Ticket Timeline</h2>

        <InfoItem
          label="Created"
          value={
            ticket.created_at
              ? new Date(ticket.created_at).toLocaleString()
              : "N/A"
          }
        />

        <div style={{ marginTop: "18px" }}>
          <InfoItem
            label="Last Updated"
            value={
              ticket.updated_at
                ? new Date(ticket.updated_at).toLocaleString()
                : "N/A"
            }
          />
        </div>
      </div>
    </div>
  );
}

/* Reusable information component */
function InfoItem({ label, value }) {
  return (
    <div
      style={{
        padding: "14px",
        backgroundColor: "#f8fafc",
        borderRadius: "8px",
      }}
    >
      <div
        style={{
          fontSize: "13px",
          color: "#64748b",
          marginBottom: "5px",
        }}
      >
        {label}
      </div>

      <div
        style={{
          fontWeight: "bold",
          color: "#111827",
        }}
      >
        {value || "N/A"}
      </div>
    </div>
  );
}

export default TicketDetails;