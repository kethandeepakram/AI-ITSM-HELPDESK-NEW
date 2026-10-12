from datetime import datetime
from app.database.mongodb import get_tickets_collection
from app.services.ai_service import analyze_ticket
from app.services.automation_service import execute_automation
from app.services.servicenow_service import create_servicenow_incident, update_servicenow_incident

def generate_ticket_id():
    collection = get_tickets_collection()
    today = datetime.now().strftime("%Y%m%d")
    count = collection.count_documents({"ticket_id": {"$regex": f"^INC-{today}-"}})
    return f"INC-{today}-{count + 1:04d}"

def create_ticket(message: str, auto_execute_self_heal: bool = True) -> dict:
    # 1. Analyze user request with AI
    analysis = analyze_ticket(message)

    # 2. Generate unique ticket identifier
    ticket_id = generate_ticket_id()

    # 3. Formulate Ticket record
    ticket = {
        "ticket_id": ticket_id,
        "message": message,
        "summary": analysis.get("summary"),
        "intent": analysis["intent"],
        "category": analysis["category"],
        "subcategory": analysis["subcategory"],
        "priority": analysis["priority"],
        "impact": analysis.get("impact", "Individual"),
        "urgency": analysis["urgency"],
        "assignment_group": analysis["assignment_group"],
        "suggested_action": analysis["suggested_action"],
        "suggested_resolution": analysis.get("suggested_resolution"),
        "automation_possible": analysis["automation_possible"],
        "automation_action": analysis.get("automation_action"),
        "software_name": analysis.get("software_name"),
        "confidence_score": analysis.get("confidence_score", 0.9),
        "should_escalate": analysis.get("should_escalate", False),
        "status": "Escalated" if analysis.get("should_escalate") else "Open",
        "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }

    # 4. Create Incident in ServiceNow
    snow_res = create_servicenow_incident(ticket)
    if snow_res.get("success"):
        ticket["servicenow_incident"] = snow_res.get("incident_number")
        ticket["servicenow_status"] = snow_res.get("status")
        ticket["servicenow_mode"] = snow_res.get("mode")

    collection = get_tickets_collection()
    result = collection.insert_one(ticket)
    ticket["_id"] = str(result.inserted_id)

    # 5. Execute Auto-Resolution / Self-Heal if eligible
    automation_result = None
    if auto_execute_self_heal and analysis["automation_possible"] and not analysis.get("should_escalate"):
        act = analysis.get("automation_action")
        if act:
            automation_result = execute_automation(
                action=act,
                ticket_id=ticket_id,
                software_name=analysis.get("software_name", "Visual Studio Code")
            )
            if automation_result.get("success"):
                new_status = "Resolved"
                ticket["status"] = new_status
                ticket["automation_result"] = automation_result
                ticket["automation_status"] = "Success"
                if automation_result.get("request_id"):
                    ticket["provisioning_request_id"] = automation_result["request_id"]

                # Update MongoDB
                collection.update_one(
                    {"ticket_id": ticket_id},
                    {
                        "$set": {
                            "status": new_status,
                            "automation_status": "Success",
                            "automation_result": automation_result,
                            "provisioning_request_id": automation_result.get("request_id"),
                            "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                        }
                    }
                )

                # The current automation service is a demo simulator. It may
                # update the local mock incident for demonstration, but must not
                # resolve a real ServiceNow incident without performing real remediation.
                if (
                    ticket.get("servicenow_incident")
                    and ticket.get("servicenow_mode") != "Live ServiceNow Instance"
                ):
                    update_servicenow_incident(
                        ticket["servicenow_incident"],
                        {
                            "state": "Resolved",
                            "close_notes": f"Demo workflow resolved the simulated incident via {act}."
                        }
                    )

    return {
        "ticket": ticket,
        "analysis": analysis,
        "servicenow": snow_res,
        "automation": automation_result
    }

def get_all_tickets_list():
    collection = get_tickets_collection()
    return list(collection.find({}, {"_id": 0}).sort("created_at", -1))