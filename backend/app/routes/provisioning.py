from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.services.automation_service import execute_automation, SOFTWARE_CATALOG
from app.database.mongodb import get_provisioning_collection

router = APIRouter(
    prefix="/api/provisioning",
    tags=["Self-Healing & Software Provisioning"]
)

class AutomationRequest(BaseModel):
    ticket_id: str
    action: str
    software_name: Optional[str] = "Visual Studio Code"

class SoftwareProvisionRequest(BaseModel):
    ticket_id: Optional[str] = "REQ-ADHOC"
    software_name: str

@router.post("/execute")
def execute_self_healing(request: AutomationRequest):
    return execute_automation(
        action=request.action,
        ticket_id=request.ticket_id,
        software_name=request.software_name
    )

@router.post("/software")
def provision_software(request: SoftwareProvisionRequest):
    return execute_automation(
        action="software_install",
        ticket_id=request.ticket_id,
        software_name=request.software_name
    )

@router.get("/catalog")
def get_catalog():
    return {
        "success": True,
        "catalog": SOFTWARE_CATALOG
    }

@router.get("/requests")
def get_provisioning_requests():
    collection = get_provisioning_collection()
    requests = list(collection.find({}, {"_id": 0}).sort("created_at", -1))

    # Migrate legacy records created by the old mock workflow. Those records
    # said "Provisioning" even though the demo flow had finished its simulated
    # steps. Keep the UI, ticket and stored request status consistent.
    for request in requests:
        workflow_steps = request.get("workflow_steps") or []
        has_legacy_mock_steps = any(
            "Mock Provisioning API" in str(step)
            or "Provisioning completed successfully" in str(step)
            for step in workflow_steps
        )
        if request.get("status") == "Provisioning" and has_legacy_mock_steps:
            request_id = request.get("request_id")
            updated_steps = [
                "1. Employee AI intent detection completed",
                f"2. Software catalogue verified: {request.get('software', 'requested software')}",
                f"3. Mock ServiceNow service request created ({request_id})",
                "4. Provisioning result simulated; no endpoint agent was contacted",
                "5. Demo workflow completed; no software was installed",
            ]
            patch = {
                "status": "Completed (Simulated)",
                "execution_mode": "SIMULATED",
                "software_installed": False,
                "servicenow_status": "Mock request created; no software installed",
                "workflow_steps": updated_steps,
            }
            collection.update_one(
                {"request_id": request_id, "status": "Provisioning"},
                {"$set": patch},
            )
            request.update(patch)

    return {
        "success": True,
        "count": len(requests),
        "requests": requests
    }