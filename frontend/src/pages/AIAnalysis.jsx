import React, { useState } from 'react';
import { api } from '../services/api';

const SAMPLE_PROMPTS = [
  "I cannot connect to VPN since this morning. Authentication keeps failing.",
  "My password has expired and I cannot sign in.",
  "How do I troubleshoot Outlook synchronization?",
  "I need Visual Studio Code installed on my laptop.",
  "My corporate Wi-Fi keeps disconnecting every 5 minutes.",
  "Can you book a flight ticket to Paris for my vacation?",
];

export default function AIAnalysis() {
  const [query, setQuery] = useState(SAMPLE_PROMPTS[0]);
  const [loading, setLoading] = useState(false);
  const [analysisData, setAnalysisData] = useState(null);
  const [error, setError] = useState('');

  const runAnalysis = async (textToAnalyze) => {
    const text = textToAnalyze || query;
    if (!text.trim() || loading) return;

    try {
      setLoading(true);
      setError('');
      const data = await api.sendChatMessage(text);
      setAnalysisData(data);
    } catch (err) {
      setError(err.message || 'Failed to analyze query');
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (score) => {
    if (score >= 0.85) return '#10b981'; // Green
    if (score >= 0.65) return '#f59e0b'; // Amber
    return '#ef4444'; // Red
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: '800', color: '#0f172a', margin: '0 0 8px 0' }}>
          🧠 AI Decisioning & Analysis Inspector
        </h1>
        <p style={{ color: '#64748b', fontSize: '15px', margin: 0 }}>
          Inspect real-time AI classification, confidence scoring, RAG source attribution, self-healing routing, and ServiceNow field mapping.
        </p>
      </div>

      {/* Query Input Box */}
      <div style={{ background: '#ffffff', borderRadius: '12px', padding: '20px', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', marginBottom: '24px' }}>
        <div style={{ marginBottom: '12px', fontSize: '13px', fontWeight: '600', color: '#475569' }}>
          SELECT A TEST PROMPT OR ENTER YOUR OWN:
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '14px' }}>
          {SAMPLE_PROMPTS.map((p, idx) => (
            <button
              key={idx}
              onClick={() => {
                setQuery(p);
                runAnalysis(p);
              }}
              style={{
                fontSize: '12px',
                padding: '6px 12px',
                borderRadius: '20px',
                border: '1px solid #cbd5e1',
                background: query === p ? '#2563eb' : '#f8fafc',
                color: query === p ? '#ffffff' : '#334155',
                cursor: 'pointer',
                fontWeight: '500',
                transition: 'all 0.15s',
              }}
            >
              {p.slice(0, 36)}...
            </button>
          ))}
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && runAnalysis()}
            placeholder="Type employee issue..."
            style={{
              flex: 1,
              padding: '12px 16px',
              borderRadius: '8px',
              border: '1px solid #cbd5e1',
              fontSize: '15px',
              outline: 'none',
            }}
          />
          <button
            onClick={() => runAnalysis()}
            disabled={loading}
            style={{
              padding: '12px 24px',
              backgroundColor: '#2563eb',
              color: '#ffffff',
              border: 'none',
              borderRadius: '8px',
              fontWeight: '600',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '14px',
            }}
          >
            {loading ? 'Analyzing...' : '⚡ Inspect AI Analysis'}
          </button>
        </div>
      </div>

      {error && (
        <div style={{ padding: '16px', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', color: '#b91c1c', marginBottom: '20px' }}>
          ⚠️ {error}
        </div>
      )}

      {/* Analysis Results View */}
      {analysisData && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '20px' }}>
          {/* Left Column: Classification & Governance */}
          <div style={{ gridColumn: 'span 7', display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* Primary Classification Card */}
            <div style={{ background: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
              <h3 style={{ margin: '0 0 16px 0', fontSize: '17px', color: '#0f172a', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span>🎯 Ticket Classification & Metadata</span>
                <span style={{
                  fontSize: '12px',
                  padding: '4px 10px',
                  borderRadius: '16px',
                  background: analysisData.intent === 'Incident' ? '#fee2e2' : '#e0e7ff',
                  color: analysisData.intent === 'Incident' ? '#991b1b' : '#3730a3',
                  fontWeight: '700'
                }}>
                  {analysisData.intent}
                </span>
              </h3>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '16px' }}>
                <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <div style={{ fontSize: '11px', color: '#64748b', fontWeight: '700', textTransform: 'uppercase' }}>Category / Subcategory</div>
                  <div style={{ fontSize: '15px', fontWeight: '600', color: '#1e293b', marginTop: '4px' }}>
                    {analysisData.category} / {analysisData.subcategory}
                  </div>
                </div>

                <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <div style={{ fontSize: '11px', color: '#64748b', fontWeight: '700', textTransform: 'uppercase' }}>Priority & Urgency</div>
                  <div style={{ fontSize: '15px', fontWeight: '600', color: '#1e293b', marginTop: '4px' }}>
                    <span style={{ color: '#dc2626' }}>{analysisData.priority}</span> ({analysisData.urgency} Urgency)
                  </div>
                </div>

                <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <div style={{ fontSize: '11px', color: '#64748b', fontWeight: '700', textTransform: 'uppercase' }}>Assignment Group</div>
                  <div style={{ fontSize: '15px', fontWeight: '600', color: '#1e293b', marginTop: '4px' }}>
                    👥 {analysisData.assignment_group}
                  </div>
                </div>

                <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <div style={{ fontSize: '11px', color: '#64748b', fontWeight: '700', textTransform: 'uppercase' }}>Self-Healing Eligibility</div>
                  <div style={{ fontSize: '15px', fontWeight: '600', color: analysisData.automation_possible ? '#16a34a' : '#64748b', marginTop: '4px' }}>
                    {analysisData.automation_possible ? `⚡ Enabled (${analysisData.automation_action})` : '🚫 Manual Handling'}
                  </div>
                </div>
              </div>

              <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '12px' }}>
                <div style={{ fontSize: '11px', color: '#64748b', fontWeight: '700', textTransform: 'uppercase' }}>AI Generated Summary</div>
                <div style={{ fontSize: '14px', color: '#0f172a', fontWeight: '500', marginTop: '4px' }}>
                  {analysisData.summary}
                </div>
              </div>

              <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <div style={{ fontSize: '11px', color: '#64748b', fontWeight: '700', textTransform: 'uppercase' }}>Suggested Resolution Plan</div>
                <div style={{ fontSize: '14px', color: '#0f172a', marginTop: '4px' }}>
                  {analysisData.suggested_resolution}
                </div>
              </div>
            </div>

            {/* AI Safety & Governance Score Meter */}
            <div style={{ background: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
              <h3 style={{ margin: '0 0 14px 0', fontSize: '17px', color: '#0f172a' }}>
                🛡️ AI Safety, Governance & Confidence
              </h3>

              <div style={{ marginBottom: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ fontSize: '14px', fontWeight: '600', color: '#334155' }}>Confidence Score</span>
                  <span style={{ fontSize: '14px', fontWeight: '700', color: getConfidenceColor(analysisData.confidence_score) }}>
                    {(analysisData.confidence_score * 100).toFixed(0)}%
                  </span>
                </div>
                <div style={{ height: '10px', background: '#e2e8f0', borderRadius: '6px', overflow: 'hidden' }}>
                  <div style={{
                    height: '100%',
                    width: `${analysisData.confidence_score * 100}%`,
                    backgroundColor: getConfidenceColor(analysisData.confidence_score),
                    borderRadius: '6px',
                    transition: 'width 0.4s ease'
                  }} />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div style={{
                  padding: '12px',
                  borderRadius: '8px',
                  background: analysisData.grounded ? '#f0fdf4' : '#fef2f2',
                  border: `1px solid ${analysisData.grounded ? '#bbf7d0' : '#fecaca'}`,
                }}>
                  <div style={{ fontSize: '12px', fontWeight: '700', color: analysisData.grounded ? '#166534' : '#991b1b' }}>
                    {analysisData.grounded ? '✅ Grounded in Knowledge Base' : '⚠️ Anti-Hallucination Guard Active'}
                  </div>
                  <div style={{ fontSize: '12px', color: '#475569', marginTop: '4px' }}>
                    {analysisData.grounded ? `Source: ${analysisData.source_used}` : 'No verified internal document. Hallucinations blocked.'}
                  </div>
                </div>

                <div style={{
                  padding: '12px',
                  borderRadius: '8px',
                  background: analysisData.should_escalate ? '#fffbeb' : '#f0fdf4',
                  border: `1px solid ${analysisData.should_escalate ? '#fde68a' : '#bbf7d0'}`,
                }}>
                  <div style={{ fontSize: '12px', fontWeight: '700', color: analysisData.should_escalate ? '#b45309' : '#166534' }}>
                    {analysisData.should_escalate ? '🚨 Human Escalation Required' : '🟢 Automated Resolution Permitted'}
                  </div>
                  <div style={{ fontSize: '12px', color: '#475569', marginTop: '4px' }}>
                    {analysisData.should_escalate ? 'Confidence below 65% or unapproved domain.' : 'Safe for automated resolution.'}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: RAG Sources & ServiceNow Mapping */}
          <div style={{ gridColumn: 'span 5', display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* ServiceNow Field Mapping */}
            <div style={{ background: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
              <h3 style={{ margin: '0 0 14px 0', fontSize: '17px', color: '#0f172a' }}>
                🔗 ServiceNow REST Field Mapping
              </h3>
              <p style={{ fontSize: '12px', color: '#64748b', margin: '0 0 12px 0' }}>
                Payload mapped automatically into ServiceNow Table API (<code>/api/now/table/incident</code>):
              </p>

              <table style={{ width: '100%', fontSize: '12px', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ background: '#f8fafc', textAlign: 'left', borderBottom: '1px solid #cbd5e1' }}>
                    <th style={{ padding: '6px' }}>ServiceNow Field</th>
                    <th style={{ padding: '6px' }}>AI Mapped Value</th>
                  </tr>
                </thead>
                <tbody>
                  <tr style={{ borderBottom: '1px solid #f1f5f9' }}>
                    <td style={{ padding: '6px', fontFamily: 'monospace', color: '#0284c7' }}>short_description</td>
                    <td style={{ padding: '6px' }}>{analysisData.summary}</td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid #f1f5f9' }}>
                    <td style={{ padding: '6px', fontFamily: 'monospace', color: '#0284c7' }}>category</td>
                    <td style={{ padding: '6px' }}>{analysisData.category}</td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid #f1f5f9' }}>
                    <td style={{ padding: '6px', fontFamily: 'monospace', color: '#0284c7' }}>subcategory</td>
                    <td style={{ padding: '6px' }}>{analysisData.subcategory}</td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid #f1f5f9' }}>
                    <td style={{ padding: '6px', fontFamily: 'monospace', color: '#0284c7' }}>priority</td>
                    <td style={{ padding: '6px', fontWeight: 'bold' }}>{analysisData.priority}</td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid #f1f5f9' }}>
                    <td style={{ padding: '6px', fontFamily: 'monospace', color: '#0284c7' }}>assignment_group</td>
                    <td style={{ padding: '6px' }}>{analysisData.assignment_group}</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '6px', fontFamily: 'monospace', color: '#0284c7' }}>urgency / impact</td>
                    <td style={{ padding: '6px' }}>{analysisData.urgency} / {analysisData.impact}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* RAG Source Attribution */}
            <div style={{ background: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
              <h3 style={{ margin: '0 0 14px 0', fontSize: '17px', color: '#0f172a' }}>
                📚 RAG Sources & Vector Attribution
              </h3>

              {analysisData.sources && analysisData.sources.length > 0 ? (
                analysisData.sources.map((item, idx) => (
                  <div key={idx} style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '10px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: '700', fontSize: '13px', color: '#1e293b' }}>
                        {item.article.title}
                      </span>
                      <span style={{ fontSize: '11px', background: '#dbeafe', color: '#1e40af', padding: '2px 8px', borderRadius: '12px', fontWeight: '700' }}>
                        {(item.score * 100).toFixed(0)}% Match
                      </span>
                    </div>
                    <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>
                      Ref: {item.article.id} | Category: {item.article.category}
                    </div>
                    <div style={{ fontSize: '12px', color: '#334155', marginTop: '6px', lineHeight: '1.4' }}>
                      {item.article.content.slice(0, 160)}...
                    </div>
                  </div>
                ))
              ) : (
                <div style={{ padding: '16px', background: '#fffbeb', borderRadius: '8px', fontSize: '13px', color: '#92400e' }}>
                  ⚠️ No relevant Knowledge Base articles found above threshold (Hallucination Guard active).
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
