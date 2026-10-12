import os
import json
import base64
import logging
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from app.config import settings
from app.database.mongodb import get_servicenow_collection

logger = logging.getLogger(__name__)

def _get_auth_header():
    if not (settings.SERVICENOW_USERNAME and settings.SERVICENOW_PASSWORD):
        return None
    token = base64.b64encode(
        f"{settings.SERVICENOW_USERNAME}:{settings.SERVICENOW_PASSWORD}".encode()
    ).decode()
    return f"Basic {token}"

def create_servicenow_incident(ticket: dict) -> dict:
    """
    Creates an Incident in ServiceNow using the AI-generated classification fields:
    - short_description
    - category / subcategory
    - priority, impact, urgency
    - assignment_group
    - correlation_id
    """
    collection = get_servicenow_collection()
    count = collection.count_documents({})
    inc_number = f"INC{1000000 + count + 1}"

    # Try live ServiceNow instance if credentials configured
    if settings.SERVICENOW_INSTANCE_URL and settings.SERVICENOW_USERNAME and not settings.SERVICENOW_MOCK_MODE:
        try:
            endpoint = f"{settings.SERVICENOW_INSTANCE_URL.rstrip('/')}/api/now/table/incident"
            payload = {
                "short_description": ticket.get("summary") or ticket.get("message"),
                "description": ticket.get("message"),
                "category": ticket.get("category"),
                "subcategory": ticket.get("subcategory"),
                "urgency": "1" if ticket.get("urgency") == "High" else "2",
                "impact": "1" if ticket.get("priority") == "P1" else "2",
                "assignment_group": ticket.get("assignment_group"),
                "correlation_id": ticket.get("ticket_id")
            }
            req = Request(
                endpoint,
                data=json.dumps(payload).encode(),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": _get_auth_header()
                },
                method="POST"
            )
            with urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())
                res = data.get("result", {})
                return {
                    "success": True,
                    "mode": "Live ServiceNow Instance",
                    "incident_number": res.get("number", inc_number),
                    "sys_id": res.get("sys_id"),
                    "status": "Created",
                    "state": "New",
                    "url": f"{settings.SERVICENOW_INSTANCE_URL.rstrip('/')}/nav_to.do?uri=incident.do?sys_id={res.get('sys_id')}",
                    "message": "Incident successfully created in live ServiceNow instance."
                }
        except Exception as e:
            logger.warning(f"Live ServiceNow incident creation failed ({e}). Reverting to mock.")

    # High-fidelity ServiceNow Mock
    mock_record = {
        "incident_number": inc_number,
        "source_ticket_id": ticket.get("ticket_id"),
        "short_description": ticket.get("summary") or ticket.get("message", "IT Issue"),
        "description": ticket.get("message"),
        "category": ticket.get("category", "General IT"),
        "subcategory": ticket.get("subcategory", "General"),
        "priority": ticket.get("priority", "P3"),
        "urgency": ticket.get("urgency", "Medium"),
        "impact": ticket.get("impact", "Individual"),
        "assignment_group": ticket.get("assignment_group", "IT Service Desk"),
        "state": "New",
        "stage": "Assigned",
        "mode": "ServiceNow Mock REST API",
        "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }

    collection.insert_one(mock_record)

    return {
        "success": True,
        "mode": "ServiceNow Mock REST API",
        "incident_number": inc_number,
        "status": "Created",
        "state": "New",
        "assignment_group": mock_record["assignment_group"],
        "priority": mock_record["priority"],
        "message": f"Incident {inc_number} created successfully and assigned to {mock_record['assignment_group']}."
    }

def update_servicenow_incident(incident_number: str, updates: dict) -> dict:
    """Updates existing ServiceNow incident status, resolution notes, etc."""
    collection = get_servicenow_collection()
    updates["updated_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    collection.update_one(
        {"incident_number": incident_number},
        {"$set": updates}
    )

    return {
        "success": True,
        "incident_number": incident_number,
        "updated_fields": list(updates.keys()),
        "status": "Updated",
        "message": f"ServiceNow incident {incident_number} updated successfully."
    }

def get_servicenow_incident(incident_number: str) -> dict:
    """Retrieves incident details from ServiceNow."""
    collection = get_servicenow_collection()
    record = collection.find_one({"incident_number": incident_number}, {"_id": 0})
    if record:
        return {"success": True, "incident": record}
    return {"success": False, "message": f"Incident {incident_number} not found"}

def create_servicenow_service_request(request_data: dict) -> dict:
    """Creates a Service Request in ServiceNow for Software Provisioning."""
    req_number = request_data.get("request_id") or f"REQ00{datetime.utcnow().strftime('%M%S')}"
    req_record = {
        "request_number": req_number,
        "short_description": f"Software Provisioning: {request_data.get('software')}",
        "software": request_data.get("software"),
        "status": "Provisioning",
        "stage": "Fulfillment",
        "state": "In Progress",
        "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }
    collection = get_servicenow_collection()
    collection.insert_one(req_record)
    return {
        "success": True,
        "request_number": req_number,
        "software": req_record["software"],
        "status": "Provisioning",
        "message": "ServiceNow Request created successfully."
    }
