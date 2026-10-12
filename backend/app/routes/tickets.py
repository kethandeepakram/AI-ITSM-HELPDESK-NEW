from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.models.ticket import TicketCreate
from app.services.ticket_service import create_ticket, get_all_tickets_list
from app.database.mongodb import get_tickets_collection
from app.services.servicenow_service import update_servicenow_incident

router = APIRouter(
    prefix="/api/tickets",
    tags=["ITSM Tickets"]
)

class TicketActionRequest(BaseModel):
    reason: Optional[str] = "Manual update"

@router.post("")
def create_new_ticket(request: TicketCreate):
    try:
        result = create_ticket(request.message)
        return jsonable_encoder({
    "success": True,
    "ticket": result["ticket"],
    "analysis": result["analysis"],
    "servicenow": result["servicenow"],
    "automation": result["automation"]
})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
def get_all_tickets():
    try:
        tickets = get_all_tickets_list()
        return {
            "success": True,
            "count": len(tickets),
            "tickets": tickets
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ticket_id}")
def get_ticket(ticket_id: str):
    collection = get_tickets_collection()
    ticket = collection.find_one({"ticket_id": ticket_id}, {"_id": 0})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"success": True, "ticket": ticket}

@router.post("/{ticket_id}/resolve")
def resolve_ticket(ticket_id: str, req: TicketActionRequest):
    collection = get_tickets_collection()
    ticket = collection.find_one({"ticket_id": ticket_id})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    collection.update_one(
        {"ticket_id": ticket_id},
        {"$set": {"status": "Resolved", "resolution_notes": req.reason}}
    )

    if ticket.get("servicenow_incident"):
        update_servicenow_incident(
            ticket["servicenow_incident"],
            {"state": "Resolved", "close_notes": req.reason}
        )

    return {"success": True, "status": "Resolved", "ticket_id": ticket_id}

@router.post("/{ticket_id}/escalate")
def escalate_ticket(ticket_id: str, req: TicketActionRequest):
    collection = get_tickets_collection()
    ticket = collection.find_one({"ticket_id": ticket_id})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    collection.update_one(
        {"ticket_id": ticket_id},
        {"$set": {"status": "Escalated", "escalation_reason": req.reason, "assignment_group": "L2 Human Engineering"}}
    )

    if ticket.get("servicenow_incident"):
        update_servicenow_incident(
            ticket["servicenow_incident"],
            {"state": "Escalated", "assignment_group": "L2 Human Engineering"}
        )

    return {"success": True, "status": "Escalated", "ticket_id": ticket_id}