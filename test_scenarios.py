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
from app.database.mongodb import LocalDatabase
from app.services.ai_service import _rule_based_classification
from app.services.llm_service import generate_ai_response

client = TestClient(app)


def test_local_database_cursor_and_upsert():
    db = LocalDatabase()
    collection = db["events"]
    collection.insert_one({"event_id": "old", "created_at": "2026-01-01"})
    collection.insert_one({"event_id": "new", "created_at": "2026-02-01"})

    latest = list(collection.find({}, {"_id": 0}).sort("created_at", -1).limit(1))
    assert len(latest) == 1
    assert latest[0]["event_id"] == "new"

    result = collection.update_one(
        {"id": "KB-test"},
        {"$set": {"title": "Test article"}},
        upsert=True,
    )
    assert result["upserted_id"] is not None
    assert collection.find_one({"id": "KB-test"})["title"] == "Test article"


def test_rule_based_safety_and_intent_guards():
    outage = _rule_based_classification(
        "The production server is down and multiple employees cannot access the application"
    )
    assert outage["priority"] == "P1"
    assert outage["should_escalate"] is True
    assert outage["automation_possible"] is False
    assert outage["automation_action"] is None
    assert outage["assignment_group"] == "Infrastructure / L2 Support"

    # A highly scored but unrelated article must never replace critical-incident handling.
    response = generate_ai_response(
        "The production server is down and multiple employees cannot access the application",
        outage,
        {
            "article": {
                "title": "Software Installation Request",
                "content": "Install the approved software from the catalog."
            },
            "score": 0.99,
        },
    )
    assert response["grounded"] is False
    assert "Critical production incident" in response["text"]
    assert "Install the approved software" not in response["text"]

    install = _rule_based_classification("Please install Microsoft Teams on my laptop")
    assert install["subcategory"] == "Software Provisioning"
    assert install["automation_action"] == "software_install"

    app_problem = _rule_based_classification("Python keeps crashing when I open my project")
    assert app_problem["subcategory"] != "Software Provisioning"
    assert app_problem["automation_action"] != "software_install"

def test_all_scenarios():
    test_local_database_cursor_and_upsert()
    test_rule_based_safety_and_intent_guards()
    print("=================================================================")
    print("RUNNING 5 MANDATORY HACKATHON LIVE DEMO SCENARIOS")
    print("=================================================================\n")

    # 1. Scenario 1: Intelligent Ticket Intake
    print("--- SCENARIO 1: Intelligent Ticket Intake ---")
    r1 = client.post("/api/demo/run/1")
    assert r1.status_code == 200, f"Scenario 1 failed: {r1.text}"
    d1 = r1.json()
    assert d1["expected_ai_output"]["category_subcategory"] == "Network / VPN"
    assert d1["expected_ai_output"]["priority"] == "P2"
    assert d1["servicenow_incident"]["success"] is True
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
    assert d2["ticket"]["status"] == "Resolved"
    assert d2["ticket"].get("automation_status") == "Success"
    assert d2["automation_result"]["success"] is True
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
    assert d3["sources_attributed"], "RAG should return a relevant Outlook source"
    assert d3["analysis"]["subcategory"] == "Email / Outlook"
    assert "Outlook" in d3["sources_attributed"][0]["title"]
    assert d3["grounded_llm_response"].strip()
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
    assert d4["ui_result"]["software"] == "Visual Studio Code"
    assert d4["servicenow_details"]["success"] is True
    assert d4["provisioning_workflow"], "Provisioning workflow steps should be returned"
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
    assert d5["analysis"]["category"] == "Out of Scope"
    assert d5["confidence_score"] < 0.65
    assert d5["escalation_required"] is True
    assert d5["is_grounded"] is False
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
