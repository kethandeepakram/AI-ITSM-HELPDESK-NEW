import React, { useState } from "react";

import Navbar from "./components/Navbar";
import Chatbot from "./components/chatbot";

import Dashboard from "./pages/Dashboard.jsx";
import SelfService from "./pages/SelfService.jsx";
import AIAnalysis from "./pages/AIAnalysis.jsx";
import KnowledgeBase from "./pages/KnowledgeBase.jsx";
import TicketDetails from "./pages/TicketDetails.jsx";

function App() {
  const [page, setPage] = useState("dashboard");
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [isChatOpen, setIsChatOpen] = useState(false);

  const renderPage = () => {
    switch (page) {
      case "self-service":
        return <SelfService onNavigate={setPage} />;

      case "ai-analysis":
        return <AIAnalysis />;

      case "knowledge-base":
        return <KnowledgeBase />;

      case "ticket-details":
        return (
          <TicketDetails
            ticket={selectedTicket}
            onBack={() => setPage("dashboard")}
          />
        );

      case "dashboard":
      default:
        return (
          <Dashboard
            onViewTicket={(ticket) => {
              setSelectedTicket(ticket);
              setPage("ticket-details");
            }}
            onNavigate={setPage}
          />
        );
    }
  };

  return (
    <div className="app" style={{ minHeight: "100vh", backgroundColor: "#f8fafc" }}>
      <Navbar activePage={page} onNavigate={setPage} />

      <div
        style={{
          display: "flex",
          alignItems: "flex-start",
          gap: "24px",
          padding: "24px 32px",
          maxWidth: "1600px",
          margin: "0 auto",
          boxSizing: "border-box",
        }}
      >
        <main
          style={{
            flex: "1 1 auto",
            minWidth: 0,
          }}
        >
          {renderPage()}
        </main>

        {/* AI chat is opened only when the floating button is clicked. */}

      {isChatOpen && (
        <div
          style={{
            position: "fixed",
            right: "24px",
            bottom: "96px",
            width: "min(390px, calc(100vw - 32px))",
            height: "min(620px, calc(100vh - 120px))",
            zIndex: 1000,
            filter: "drop-shadow(0 12px 28px rgba(15, 23, 42, 0.22))",
          }}
        >
          <Chatbot onClose={() => setIsChatOpen(false)} />
        </div>
      )}

      <button
        type="button"
        aria-label={isChatOpen ? "Close AI helpdesk chat" : "Open AI helpdesk chat"}
        title={isChatOpen ? "Close AI chat" : "Chat with AI helpdesk"}
        onClick={() => setIsChatOpen((open) => !open)}
        style={{
          position: "fixed",
          right: "24px",
          bottom: "24px",
          width: "60px",
          height: "60px",
          borderRadius: "18px",
          border: "none",
          background: isChatOpen ? "#0f172a" : "#16a34a",
          color: "#ffffff",
          fontSize: "28px",
          fontWeight: 700,
          cursor: "pointer",
          boxShadow: "0 8px 24px rgba(15, 23, 42, 0.28)",
          zIndex: 1001,
          display: "grid",
          placeItems: "center",
        }}
      >
        {isChatOpen ? "×" : "✚"}
      </button>
      </div>
    </div>
  );
}

export default App;