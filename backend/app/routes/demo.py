from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_service import analyze_ticket
from app.services.rag_service import search_knowledge_base
from app.services.llm_service import generate_ai_response
from app.services.ticket_service import create_ticket
from app.services.automation_service import execute_automation
from app.services.servicenow_service import create_servicenow_incident, create_servicenow_service_request

router = APIRouter(
    prefix="/api/demo",
    tags=["Hackathon Live Demo Scenarios"]
)

DEMO_SCENARIOS = [
    {
        "id": 1,
        "name": "Intelligent Ticket Intake",
        "prompt": "I cannot connect to VPN since this morning. Authentication keeps failing.",
        "description": "Employee enters VPN issue -> AI classifies intent, category, priority, assignment -> Creates ServiceNow Incident."
    },
    {
        "id": 2,
        "name": "Auto Resolution / Self-Heal Agent",
        "prompt": "My password has expired.",
        "description": "Identify -> Diagnose -> Knowledge Search -> Determine Automation -> Execute -> Validate -> Update ServiceNow -> Audit Trail."
    },
    {
        "id": 3,
        "name": "Knowledge Management Automation (RAG)",
        "prompt": "How do I troubleshoot Outlook synchronization?",
        "description": "Vector Semantic Search -> LLM Grounded Generation -> Display Knowledge Sources & Attribution."
    },
    {
        "id": 4,
        "name": "Software Provisioning Automation",
        "prompt": "I need Visual Studio Code installed on my laptop.",
        "description": "AI Intent Detection -> Software Catalogue verification -> ServiceNow Request REQ001245 -> Mock Provisioning API -> Status Update."
    },
    {
        "id": 5,
        "name": "AI Safety, Governance & Escalation",
        "prompt": "Can you book a flight ticket to Paris for my vacation?",
        "description": "Unsupported question -> No hallucination policy -> Confidence check -> Escalation to Human / ServiceNow Ticket option."
    }
]

@router.get("/scenarios")
def list_scenarios():
    return {
        "success": True,
        "scenarios": DEMO_SCENARIOS
    }

@router.post("/run/{scenario_id}")
def run_scenario(scenario_id: int):
    if scenario_id == 1:
        prompt = "I cannot connect to VPN since this morning. Authentication keeps failing."
        analysis = analyze_ticket(prompt)
        rag_results = search_knowledge_base(prompt, top_k=2)
        ticket_res = create_ticket(prompt, auto_execute_self_heal=False)

        return {
            "scenario_id": 1,
            "scenario_name": "Intelligent Ticket Intake",
            "prompt": prompt,
            "expected_ai_output": {
                "intent": analysis["intent"],
                "category_subcategory": f"{analysis['category']} / {analysis['subcategory']}",
                "priority": analysis["priority"],
                "impact_urgency": f"{analysis['impact']} / {analysis['urgency']}",
                "assignment_group": analysis["assignment_group"],
                "summary": analysis["summary"],
                "suggested_resolution": analysis["suggested_resolution"]
            },
            "rag_context": rag_results[0] if rag_results else None,
            "servicenow_incident": ticket_res["servicenow"],
            "ticket": ticket_res["ticket"],
            "status": "Success"
        }

    elif scenario_id == 2:
        prompt = "My password has expired."
        analysis = analyze_ticket(prompt)
        rag_results = search_knowledge_base(prompt, top_k=1)
        ticket_res = create_ticket(prompt, auto_execute_self_heal=True)

        return {
            "scenario_id": 2,
            "scenario_name": "Auto Resolution / Self-Heal Agent",
            "prompt": prompt,
            "workflow_executed": [
                "1. Identify: Detected expired password credential",
                "2. Diagnose: Verified user account in IAM directory",
                "3. Knowledge Search: Retrieved KB1002 (Password Reset Guide)",
                "4. Determine Automation: Identified 'password_reset' action as eligible",
                "5. Execute: Triggered automated reset workflow",
                "6. Validate: OTP generated & password policy compliance verified",
                "7. Update ServiceNow: Incident updated to Resolved"
            ],
            "analysis": analysis,
            "knowledge_used": rag_results[0] if rag_results else None,
            "automation_result": ticket_res.get("automation"),
            "ticket": ticket_res["ticket"],
            "status": "Resolved"
        }

    elif scenario_id == 3:
        prompt = "How do I troubleshoot Outlook synchronization?"
        analysis = analyze_ticket(prompt)
        rag_results = search_knowledge_base(prompt, top_k=3)
        llm_res = generate_ai_response(prompt, analysis, rag_results[0] if rag_results else None)

        return {
            "scenario_id": 3,
            "scenario_name": "Knowledge Management Automation (RAG)",
            "prompt": prompt,
            "analysis": analysis,
            "vector_search_results": rag_results,
            "grounded_llm_response": llm_res["text"],
            "sources_attributed": [
                {"title": r["article"]["title"], "source": r["article"]["source"], "score": r["score"]}
                for r in rag_results
            ],
            "status": "Success"
        }

    elif scenario_id == 4:
        prompt = "I need Visual Studio Code installed on my laptop."
        analysis = analyze_ticket(prompt)
        software_name = analysis.get("software_name") or "Visual Studio Code"
        auto_res = execute_automation(action="software_install", ticket_id="TICKET-PROV-001", software_name=software_name)
        snow_res = create_servicenow_service_request({
            "request_id": auto_res.get("request_id", "REQ001245"),
            "software": software_name
        })

        return {
            "scenario_id": 4,
            "scenario_name": "Software Provisioning Automation",
            "prompt": prompt,
            "ui_result": {
                "request_id": auto_res.get("request_id", "REQ001245"),
                "software": software_name,
                "status": "Provisioning",
                "servicenow": "Request created successfully"
            },
            "analysis": analysis,
            "provisioning_workflow": auto_res.get("workflow"),
            "servicenow_details": snow_res,
            "status": "Provisioning Dispatched"
        }

    elif scenario_id == 5:
        prompt = "Can you book a flight ticket to Paris for my vacation?"
        analysis = analyze_ticket(prompt)
        rag_results = search_knowledge_base(prompt, top_k=3)
        llm_res = generate_ai_response(prompt, analysis, rag_results[0] if rag_results else None)

        return {
            "scenario_id": 5,
            "scenario_name": "AI Safety, Governance & Escalation",
            "prompt": prompt,
            "analysis": analysis,
            "confidence_score": analysis.get("confidence_score"),
            "is_grounded": llm_res["grounded"],
            "no_hallucination_guard": "ACTIVATED: Out-of-domain request rejected",
            "ai_response": llm_res["text"],
            "escalation_required": analysis.get("should_escalate", True),
            "suggested_action": "Escalate to Human IT Service Desk or create ServiceNow ticket for manual handling",
            "status": "Escalated to Human Workflow"
        }

    return {"error": "Invalid scenario ID"}
