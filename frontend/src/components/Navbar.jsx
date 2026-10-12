import React from "react";

function Navbar({ activePage, onNavigate }) {
  const navItems = [
    { id: "dashboard", label: "📊 ITSM Dashboard", badge: null },
    { id: "self-service", label: "🙋 Employee Self-Service", badge: null },
    { id: "ai-analysis", label: "🧠 AI Analysis Inspector", badge: "Live" },
    { id: "knowledge-base", label: "📚 Knowledge Base & RAG", badge: null },
  ];

  return (
    <nav
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "14px 32px",
        background: "#0f172a",
        color: "white",
        boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
        position: "sticky",
        top: 0,
        zIndex: 1000,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <div style={{
          width: "36px",
          height: "36px",
          borderRadius: "8px",
          background: "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontWeight: "800",
          fontSize: "18px"
        }}>
          S
        </div>
        <div>
          <h2 style={{ margin: 0, fontSize: "17px", fontWeight: "800", letterSpacing: "0.3px" }}>
            SORIM.Ai <span style={{ fontWeight: "400", color: "#94a3b8" }}>| Intelligent Helpdesk</span>
          </h2>
          <div style={{ fontSize: "11px", color: "#64748b" }}>AI-Powered ITSM Automation Platform</div>
        </div>
      </div>

      <div style={{ display: "flex", gap: "8px" }}>
        {navItems.map((item) => {
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "6px",
                padding: "8px 16px",
                backgroundColor: isActive ? "#1e293b" : "transparent",
                color: isActive ? "#38bdf8" : "#cbd5e1",
                border: isActive ? "1px solid #334155" : "1px solid transparent",
                borderRadius: "8px",
                fontSize: "13px",
                fontWeight: isActive ? "700" : "500",
                cursor: "pointer",
                transition: "all 0.15s ease",
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.backgroundColor = "#1e293b";
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.backgroundColor = "transparent";
              }}
            >
              <span>{item.label}</span>
              {item.badge && (
                <span style={{
                  fontSize: "10px",
                  background: "#0284c7",
                  color: "#ffffff",
                  padding: "1px 6px",
                  borderRadius: "10px",
                  fontWeight: "700"
                }}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
}

export default Navbar;