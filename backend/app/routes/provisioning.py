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
    return {
        "success": True,
        "count": len(requests),
        "requests": requests
    }