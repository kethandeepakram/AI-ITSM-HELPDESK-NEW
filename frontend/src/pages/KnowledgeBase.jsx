import React, { useState, useEffect } from "react";
import { api } from "../services/api";

const CATEGORIES = ["All", "Network", "Account & Access", "Software", "Hardware"];

export default function KnowledgeBase() {
  const [articles, setArticles] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedArticle, setSelectedArticle] = useState(null);

  useEffect(() => {
    loadArticles();
  }, []);

  const loadArticles = async () => {
    try {
      const res = await api.getKnowledgeArticles();
      setArticles(res.articles || []);
      if (res.articles && res.articles.length > 0) {
        setSelectedArticle(res.articles[0]);
      }
    } catch (err) {
      console.error("Failed to load knowledge articles:", err);
    }
  };

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!searchQuery.trim()) {
      setSearchResults(null);
      return;
    }

    try {
      setLoading(true);
      const res = await api.searchKnowledge(searchQuery.trim());
      setSearchResults(res.results || []);
      if (res.results && res.results.length > 0) {
        setSelectedArticle(res.results[0].article);
      }
    } catch (err) {
      console.error("RAG search failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const filteredArticles = articles.filter((a) => {
    if (selectedCategory === "All") return true;
    return a.category === selectedCategory;
  });

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto", fontFamily: "system-ui, -apple-system, sans-serif" }}>
      {/* Header */}
      <div style={{ marginBottom: "20px" }}>
        <h1 style={{ fontSize: "28px", fontWeight: "800", color: "#0f172a", margin: "0 0 6px 0" }}>
          📚 Enterprise Knowledge Base & RAG Engine
        </h1>
        <p style={{ color: "#64748b", fontSize: "14px", margin: 0 }}>
          Approved enterprise IT support articles indexed with vector embeddings for semantic retrieval and grounded LLM reasoning.
        </p>
      </div>

      {/* Semantic Search Box */}
      <form onSubmit={handleSearch} style={{ background: "#ffffff", padding: "16px 20px", borderRadius: "12px", border: "1px solid #e2e8f0", boxShadow: "0 1px 3px rgba(0,0,0,0.05)", marginBottom: "20px" }}>
        <div style={{ display: "flex", gap: "10px" }}>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="🔎 Test RAG Semantic Retrieval (e.g., 'How do I troubleshoot Outlook synchronization?')"
            style={{
              flex: 1,
              padding: "12px 16px",
              borderRadius: "8px",
              border: "1px solid #cbd5e1",
              fontSize: "14px",
              outline: "none",
            }}
          />
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: "12px 24px",
              backgroundColor: "#2563eb",
              color: "#ffffff",
              border: "none",
              borderRadius: "8px",
              fontWeight: "700",
              cursor: loading ? "not-allowed" : "pointer",
              fontSize: "14px",
            }}
          >
            {loading ? "Searching..." : "Vector Search"}
          </button>
          {searchResults && (
            <button
              type="button"
              onClick={() => {
                setSearchResults(null);
                setSearchQuery("");
              }}
              style={{
                padding: "12px 16px",
                backgroundColor: "#f1f5f9",
                border: "1px solid #cbd5e1",
                borderRadius: "8px",
                cursor: "pointer",
                fontSize: "13px",
              }}
            >
              Clear
            </button>
          )}
        </div>
      </form>

      {/* RAG Results Notice */}
      {searchResults && (
        <div style={{ background: "#eff6ff", border: "1px solid #bfdbfe", padding: "14px 18px", borderRadius: "10px", marginBottom: "20px" }}>
          <div style={{ fontWeight: "700", color: "#1e40af", fontSize: "14px", marginBottom: "4px" }}>
            🎯 RAG Semantic Vector Retrieval: Found {searchResults.length} matching document chunks
          </div>
          <div style={{ fontSize: "12px", color: "#3b82f6" }}>
            Query evaluated across dense vector embeddings & sparse keyword indexes.
          </div>
        </div>
      )}

      {/* Categories Bar */}
      {!searchResults && (
        <div style={{ display: "flex", gap: "8px", marginBottom: "20px", flexWrap: "wrap" }}>
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              style={{
                padding: "8px 16px",
                borderRadius: "20px",
                border: selectedCategory === cat ? "1px solid #2563eb" : "1px solid #cbd5e1",
                backgroundColor: selectedCategory === cat ? "#2563eb" : "#ffffff",
                color: selectedCategory === cat ? "#ffffff" : "#475569",
                fontWeight: "600",
                fontSize: "13px",
                cursor: "pointer",
                transition: "all 0.15s",
              }}
            >
              {cat}
            </button>
          ))}
        </div>
      )}

      {/* Main Grid: Articles List & Reader */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(12, 1fr)", gap: "20px" }}>
        {/* Left Column: List */}
        <div style={{ gridColumn: "span 5", display: "flex", flexDirection: "column", gap: "10px", maxHeight: "650px", overflowY: "auto" }}>
          {(searchResults ? searchResults.map((r) => r.article) : filteredArticles).map((article, idx) => {
            const isSelected = selectedArticle?.id === article.id;
            const searchItem = searchResults ? searchResults.find((r) => r.article.id === article.id) : null;

            return (
              <div
                key={article.id || idx}
                onClick={() => setSelectedArticle(article)}
                style={{
                  background: isSelected ? "#f0f9ff" : "#ffffff",
                  border: isSelected ? "2px solid #0284c7" : "1px solid #e2e8f0",
                  borderRadius: "10px",
                  padding: "14px 16px",
                  cursor: "pointer",
                  boxShadow: "0 1px 2px rgba(0,0,0,0.04)",
                  transition: "all 0.15s",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" }}>
                  <span style={{ fontSize: "11px", fontWeight: "700", color: "#0284c7" }}>
                    {article.id}
                  </span>
                  {searchItem && (
                    <span style={{ fontSize: "11px", background: "#dbeafe", color: "#1e40af", padding: "1px 6px", borderRadius: "10px", fontWeight: "700" }}>
                      {(searchItem.score * 100).toFixed(0)}% Score
                    </span>
                  )}
                </div>

                <div style={{ fontWeight: "700", fontSize: "14px", color: "#0f172a", marginBottom: "4px" }}>
                  {article.title}
                </div>

                <div style={{ fontSize: "12px", color: "#64748b" }}>
                  📁 {article.category}
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Column: Article Details */}
        <div style={{ gridColumn: "span 7" }}>
          {selectedArticle ? (
            <div style={{ background: "#ffffff", borderRadius: "12px", border: "1px solid #e2e8f0", padding: "24px", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                <span style={{ fontSize: "12px", background: "#e0e7ff", color: "#3730a3", padding: "4px 10px", borderRadius: "12px", fontWeight: "700" }}>
                  {selectedArticle.category} / {selectedArticle.subcategory || selectedArticle.category}
                </span>
                <span style={{ fontSize: "12px", color: "#64748b" }}>
                  Document Ref: <strong>{selectedArticle.id}</strong>
                </span>
              </div>

              <h2 style={{ fontSize: "22px", color: "#0f172a", margin: "0 0 16px 0" }}>
                {selectedArticle.title}
              </h2>

              <div style={{ padding: "12px 16px", background: "#f8fafc", borderRadius: "8px", border: "1px solid #e2e8f0", marginBottom: "20px" }}>
                <div style={{ fontSize: "11px", fontWeight: "700", color: "#64748b", textTransform: "uppercase" }}>Source Attribution</div>
                <div style={{ fontSize: "13px", color: "#1e293b", fontWeight: "600", marginTop: "2px" }}>
                  {selectedArticle.source || `IT Knowledge Base / ${selectedArticle.id}`}
                </div>
              </div>

              <div style={{ fontSize: "14px", color: "#334155", lineHeight: "1.7", whiteSpace: "pre-line", marginBottom: "24px" }}>
                {selectedArticle.content}
              </div>

              {selectedArticle.keywords && (
                <div>
                  <div style={{ fontSize: "12px", fontWeight: "700", color: "#64748b", marginBottom: "8px" }}>
                    INDEXED KEYWORDS & EMBEDDING TOKENS:
                  </div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                    {selectedArticle.keywords.map((kw, i) => (
                      <span key={i} style={{ fontSize: "11px", background: "#f1f5f9", color: "#475569", padding: "2px 8px", borderRadius: "6px" }}>
                        #{kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div style={{ padding: "40px", textAlign: "center", color: "#94a3b8", background: "#ffffff", borderRadius: "12px", border: "1px solid #e2e8f0" }}>
              Select an article to view details
            </div>
          )}
        </div>
      </div>
    </div>
  );
}