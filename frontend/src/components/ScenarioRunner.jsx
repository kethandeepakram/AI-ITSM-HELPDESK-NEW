import React, { useState } from 'react';
import { api } from '../services/api';

const SCENARIOS = [
  { id: 1, title: '1. Intelligent Ticket Intake', subtitle: 'VPN Authentication Failure -> ServiceNow INC', icon: '🎫' },
  { id: 2, title: '2. Auto Resolution / Self-Heal', subtitle: 'Password Expired -> Self-Heal -> Audit Log', icon: '⚡' },
  { id: 3, title: '3. Knowledge Management (RAG)', subtitle: 'Outlook Sync -> Vector Search -> Grounded LLM', icon: '📚' },
  { id: 4, title: '4. Software Provisioning', subtitle: 'Visual Studio Code -> Catalogue -> ServiceNow REQ', icon: '💻' },
  { id: 5, title: '5. AI Safety & Escalation', subtitle: 'Unknown Query -> Hallucination Guard -> Escalate', icon: '🛡️' },
];

export default function ScenarioRunner({ onScenarioExecuted }) {
  const [runningId, setRunningId] = useState(null);
  const [activeModalData, setActiveModalData] = useState(null);

  const handleRun = async (id) => {
    try {
      setRunningId(id);
      const res = await api.runDemoScenario(id);
      setActiveModalData(res);
      if (onScenarioExecuted) onScenarioExecuted(res);
    } catch (err) {
      alert(`Scenario execution failed: ${err.message}`);
    } finally {
      setRunningId(null);
    }
  };

  return (
    <div style={{
      background: 'linear-gradient(90deg, #1e293b 0%, #0f172a 100%)',
      padding: '14px 24px',
      borderRadius: '12px',
      color: '#ffffff',
      marginBottom: '24px',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '18px' }}>🚀</span>
          <span style={{ fontWeight: '800', fontSize: '15px', letterSpacing: '0.5px' }}>
            HACKATHON LIVE DEMO LAUNCHER (SECTION 11)
          </span>
        </div>
        <span style={{ fontSize: '12px', color: '#94a3b8' }}>
          Click any scenario to demonstrate the complete end-to-end automated pipeline
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px' }}>
        {SCENARIOS.map((s) => (
          <button
            key={s.id}
            onClick={() => handleRun(s.id)}
            disabled={runningId !== null}
            style={{
              display: 'flex',
              flexDirection: 'column',
              textAlign: 'left',
              padding: '10px 14px',
              backgroundColor: runningId === s.id ? '#3b82f6' : '#334155',
              border: '1px solid #475569',
              borderRadius: '8px',
              color: '#ffffff',
              cursor: runningId !== null ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s',
            }}
          >
            <div style={{ fontSize: '13px', fontWeight: '700', marginBottom: '2px' }}>
              {s.icon} {s.title}
            </div>
            <div style={{ fontSize: '11px', color: '#cbd5e1' }}>
              {runningId === s.id ? 'Running verification...' : s.subtitle}
            </div>
          </button>
        ))}
      </div>

      {/* Scenario Execution Modal */}
      {activeModalData && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.65)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          padding: '20px',
        }}>
          <div style={{
            background: '#ffffff',
            color: '#0f172a',
            borderRadius: '16px',
            maxWidth: '750px',
            width: '100%',
            maxHeight: '90vh',
            overflowY: 'auto',
            padding: '28px',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.25)',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid #e2e8f0', paddingBottom: '12px' }}>
              <h2 style={{ margin: 0, fontSize: '20px', color: '#1e293b' }}>
                🎉 Scenario {activeModalData.scenario_id}: {activeModalData.scenario_name}
              </h2>
              <button
                onClick={() => setActiveModalData(null)}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '22px',
                  cursor: 'pointer',
                  color: '#64748b',
                }}
              >
                ✕
              </button>
            </div>

            <div style={{ background: '#f8fafc', padding: '14px', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '16px' }}>
              <div style={{ fontSize: '11px', fontWeight: '700', color: '#64748b' }}>EMPLOYEE INPUT PROMPT:</div>
              <div style={{ fontSize: '15px', fontWeight: '600', color: '#0f172a', marginTop: '4px' }}>
                "{activeModalData.prompt}"
              </div>
            </div>

            {/* Scenario 1 Content */}
            {activeModalData.scenario_id === 1 && (
              <div>
                <h4 style={{ margin: '0 0 10px 0', color: '#166534' }}>✅ AI Extraction & ServiceNow Incident Created</h4>
                <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '14px', marginBottom: '14px', fontSize: '13px', lineHeight: '1.6' }}>
                  <div><strong>Intent:</strong> {activeModalData.expected_ai_output.intent}</div>
                  <div><strong>Category / Sub-category:</strong> {activeModalData.expected_ai_output.category_subcategory}</div>
                  <div><strong>Priority:</strong> {activeModalData.expected_ai_output.priority}</div>
                  <div><strong>Impact / Urgency:</strong> {activeModalData.expected_ai_output.impact_urgency}</div>
                  <div><strong>Assignment Group:</strong> {activeModalData.expected_ai_output.assignment_group}</div>
                  <div><strong>Summary:</strong> {activeModalData.expected_ai_output.summary}</div>
                  <div><strong>Suggested Resolution:</strong> {activeModalData.expected_ai_output.suggested_resolution}</div>
                  <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #bbf7d0', color: '#14532d', fontWeight: '700' }}>
                    ServiceNow Incident: {activeModalData.servicenow_incident.incident_number} ({activeModalData.servicenow_incident.mode})
                  </div>
                </div>
              </div>
            )}

            {/* Scenario 2 Content */}
            {activeModalData.scenario_id === 2 && (
              <div>
                <h4 style={{ margin: '0 0 10px 0', color: '#166534' }}>⚡ Automated Self-Healing Execution Flow</h4>
                <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '14px', marginBottom: '14px' }}>
                  {activeModalData.workflow_executed.map((step, idx) => (
                    <div key={idx} style={{ fontSize: '13px', marginBottom: '6px', color: '#166534', fontWeight: '500' }}>
                      {step}
                    </div>
                  ))}
                  <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #bbf7d0', fontSize: '13px' }}>
                    ServiceNow Status: <strong>{activeModalData.ticket.servicenow_incident} updated to {activeModalData.status}</strong>
                  </div>
                </div>
              </div>
            )}

            {/* Scenario 3 Content */}
            {activeModalData.scenario_id === 3 && (
              <div>
                <h4 style={{ margin: '0 0 10px 0', color: '#1e40af' }}>📚 Vector Semantic Search & Grounded Response</h4>
                <div style={{ background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '8px', padding: '14px', marginBottom: '14px', fontSize: '13px' }}>
                  <div style={{ fontWeight: '700', marginBottom: '6px' }}>Retrieved Enterprise Knowledge Sources:</div>
                  {activeModalData.sources_attributed.map((s, idx) => (
                    <div key={idx} style={{ color: '#1e40af', marginBottom: '4px' }}>
                      • <strong>{s.title}</strong> (Relevance: {(s.score * 100).toFixed(0)}%)
                    </div>
                  ))}
                  <div style={{ marginTop: '12px', padding: '10px', background: '#ffffff', borderRadius: '6px', whiteSpace: 'pre-line', color: '#334155' }}>
                    {activeModalData.grounded_llm_response}
                  </div>
                </div>
              </div>
            )}

            {/* Scenario 4 Content */}
            {activeModalData.scenario_id === 4 && (
              <div>
                <h4 style={{ margin: '0 0 10px 0', color: '#7c3aed' }}>💻 Automated Software Provisioning Pipeline</h4>
                <div style={{ background: '#f5f3ff', border: '1px solid #ddd6fe', borderRadius: '8px', padding: '14px', marginBottom: '14px', fontSize: '13px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px' }}>
                    <div>Request ID: <strong>{activeModalData.ui_result.request_id}</strong></div>
                    <div>Software: <strong>{activeModalData.ui_result.software}</strong></div>
                    <div>Status: <span style={{ color: '#7c3aed', fontWeight: '700' }}>{activeModalData.ui_result.status}</span></div>
                    <div>ServiceNow: <strong>{activeModalData.ui_result.servicenow}</strong></div>
                  </div>
                  <div style={{ fontWeight: '700', marginBottom: '4px' }}>Workflow Execution Steps:</div>
                  {activeModalData.provisioning_workflow.map((w, idx) => (
                    <div key={idx} style={{ fontSize: '12px', color: '#5b21b6', marginBottom: '2px' }}>{w}</div>
                  ))}
                </div>
              </div>
            )}

            {/* Scenario 5 Content */}
            {activeModalData.scenario_id === 5 && (
              <div>
                <h4 style={{ margin: '0 0 10px 0', color: '#b91c1c' }}>🛡️ AI Safety & Anti-Hallucination Policy Triggered</h4>
                <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', padding: '14px', marginBottom: '14px', fontSize: '13px' }}>
                  <div>Confidence Score: <strong style={{ color: '#dc2626' }}>{(activeModalData.confidence_score * 100).toFixed(0)}% (Below 65% Threshold)</strong></div>
                  <div>Policy Action: <strong>{activeModalData.no_hallucination_guard}</strong></div>
                  <div>Human Escalation: <strong>{activeModalData.escalation_required ? 'YES (Automatic L2 Queue)' : 'NO'}</strong></div>
                  <div style={{ marginTop: '10px', padding: '10px', background: '#ffffff', borderRadius: '6px', color: '#991b1b', whiteSpace: 'pre-line' }}>
                    {activeModalData.ai_response}
                  </div>
                </div>
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '16px' }}>
              <button
                onClick={() => setActiveModalData(null)}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#1e293b',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '8px',
                  fontWeight: '600',
                  cursor: 'pointer',
                }}
              >
                Close Verification
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
