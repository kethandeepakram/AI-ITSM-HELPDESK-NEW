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

        <aside
          style={{
            width: "380px",
            flex: "0 0 380px",
            position: "sticky",
            top: "84px",
            alignSelf: "flex-start",
          }}
        >
          <Chatbot />
        </aside>
      </div>
    </div>
  );
}

export default App;