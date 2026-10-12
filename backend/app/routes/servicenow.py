from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.services.servicenow_service import (
    create_servicenow_incident,
    get_servicenow_incident,
    update_servicenow_incident,
    create_servicenow_service_request
)
from app.database.mongodb import get_servicenow_collection

router = APIRouter(
    prefix="/api/servicenow",
    tags=["ServiceNow Integration"]
)

class IncidentUpdateRequest(BaseModel):
    state: Optional[str] = "Resolved"
    close_notes: Optional[str] = "Updated via API"

@router.post("/create")
def create_incident(ticket: dict):
    try:
        return create_servicenow_incident(ticket)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/incidents")
def list_incidents():
    collection = get_servicenow_collection()
    incidents = list(collection.find({}, {"_id": 0}).sort("created_at", -1))
    return {
        "success": True,
        "count": len(incidents),
        "incidents": incidents
    }

@router.get("/incident/{incident_number}")
def fetch_incident(incident_number: str):
    res = get_servicenow_incident(incident_number)
    if not res.get("success"):
        raise HTTPException(status_code=404, detail="Incident not found")
    return res

@router.patch("/incident/{incident_number}")
def patch_incident(incident_number: str, req: IncidentUpdateRequest):
    return update_servicenow_incident(
        incident_number=incident_number,
        updates=req.dict(exclude_unset=True)
    )

@router.post("/request")
def create_service_request(req_data: dict):
    return create_servicenow_service_request(req_data)