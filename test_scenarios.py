import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_all_scenarios():
    print("=================================================================")
    print("RUNNING 5 MANDATORY HACKATHON LIVE DEMO SCENARIOS")
    print("=================================================================\n")

    # 1. Scenario 1: Intelligent Ticket Intake
    print("--- SCENARIO 1: Intelligent Ticket Intake ---")
    r1 = client.post("/api/demo/run/1")
    assert r1.status_code == 200, f"Scenario 1 failed: {r1.text}"
    d1 = r1.json()
    print(f"Prompt: {d1['prompt']}")
    print(f"Expected AI Output:")
    for k, v in d1['expected_ai_output'].items():
        print(f"  {k}: {v}")
    print(f"ServiceNow Incident Created: {d1['servicenow_incident']['incident_number']}")
    print("-> SCENARIO 1 PASSED!\n")

    # 2. Scenario 2: Self-Healing
    print("--- SCENARIO 2: Self-Healing Agent ---")
    r2 = client.post("/api/demo/run/2")
    assert r2.status_code == 200, f"Scenario 2 failed: {r2.text}"
    d2 = r2.json()
    print(f"Prompt: {d2['prompt']}")
    print("Workflow executed:")
    for step in d2['workflow_executed']:
        print(f"  {step}")
    print(f"Action Status: {d2['status']}")
    print(f"ServiceNow Incident Number: {d2['ticket'].get('servicenow_incident')}")
    print("-> SCENARIO 2 PASSED!\n")

    # 3. Scenario 3: RAG
    print("--- SCENARIO 3: Knowledge Management Automation (RAG) ---")
    r3 = client.post("/api/demo/run/3")
    assert r3.status_code == 200, f"Scenario 3 failed: {r3.text}"
    d3 = r3.json()
    print(f"Prompt: {d3['prompt']}")
    print("Retrieved Sources:")
    for s in d3['sources_attributed']:
        print(f"  - {s['title']} (Score: {s['score']})")
    print(f"Grounded Response Preview:\n{d3['grounded_llm_response'][:200]}...")
    print("-> SCENARIO 3 PASSED!\n")

    # 4. Scenario 4: Software Provisioning
    print("--- SCENARIO 4: Software Provisioning Automation ---")
    r4 = client.post("/api/demo/run/4")
    assert r4.status_code == 200, f"Scenario 4 failed: {r4.text}"
    d4 = r4.json()
    print(f"Prompt: {d4['prompt']}")
    print(f"UI Result:")
    for k, v in d4['ui_result'].items():
        print(f"  {k}: {v}")
    print("Workflow:")
    for step in d4['provisioning_workflow']:
        print(f"  {step}")
    print("-> SCENARIO 4 PASSED!\n")

    # 5. Scenario 5: Unknown Question & AI Safety
    print("--- SCENARIO 5: AI Safety, Governance & Escalation ---")
    r5 = client.post("/api/demo/run/5")
    assert r5.status_code == 200, f"Scenario 5 failed: {r5.text}"
    d5 = r5.json()
    print(f"Prompt: {d5['prompt']}")
    print(f"Confidence Score: {d5['confidence_score']} (Below threshold)")
    print(f"Grounded in KB: {d5['is_grounded']}")
    print(f"Hallucination Guard: {d5['no_hallucination_guard']}")
    print(f"Escalation Required: {d5['escalation_required']}")
    print(f"Response: {d5['ai_response'][:180]}...")
    print("-> SCENARIO 5 PASSED!\n")

    print("=================================================================")
    print("ALL 5 HACKATHON SCENARIOS TESTED AND PASSED WITH 100% SUCCESS!")
    print("=================================================================")

if __name__ == "__main__":
    test_all_scenarios()
