import os
import json
import base64
import logging
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.parse import quote, urlencode
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

def _live_servicenow_enabled() -> bool:
    return bool(
        settings.SERVICENOW_INSTANCE_URL
        and settings.SERVICENOW_USERNAME
        and settings.SERVICENOW_PASSWORD
        and not settings.SERVICENOW_MOCK_MODE
    )


def _live_table_request(
    table: str,
    method: str = "GET",
    payload: dict | None = None,
    query: str | None = None,
    sys_id: str | None = None,
) -> dict:
    """Call the live ServiceNow Table API and return its result object."""
    base_url = settings.SERVICENOW_INSTANCE_URL.rstrip("/")
    endpoint = f"{base_url}/api/now/table/{quote(table, safe='')}"
    if sys_id:
        endpoint += f"/{quote(sys_id, safe='')}"
    if query:
        endpoint += "?" + urlencode({"sysparm_query": query, "sysparm_limit": 1})

    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {
        "Accept": "application/json",
        "Authorization": _get_auth_header(),
    }
    if data is not None:
        headers["Content-Type"] = "application/json"

    request = Request(endpoint, data=data, headers=headers, method=method)
    with urlopen(request, timeout=8) as response:
        response_data = json.loads(response.read().decode("utf-8"))
    return response_data.get("result", {})


def list_servicenow_incidents() -> dict:
    """Return live incidents when live mode is enabled; otherwise return mock records."""
    if _live_servicenow_enabled():
        try:
            result = _live_table_request(
                "incident",
                query="ORDERBYDESCsys_updated_on",
            )
            # Table API query returns a list when querying a table.
            incidents = result if isinstance(result, list) else ([result] if result else [])
            return {"success": True, "count": len(incidents), "incidents": incidents, "mode": "Live ServiceNow Instance"}
        except Exception as exc:
            logger.warning("Unable to list live ServiceNow incidents: %s", exc)
            return {"success": False, "count": 0, "incidents": [], "mode": "Live ServiceNow Instance", "error": str(exc)}

    collection = get_servicenow_collection()
    incidents = list(collection.find({}, {"_id": 0}).sort("created_at", -1))
    return {"success": True, "count": len(incidents), "incidents": incidents, "mode": "ServiceNow Mock REST API"}

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
    if _live_servicenow_enabled():
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
    """Update a live ServiceNow incident or the local mock record."""
    safe_updates = dict(updates)
    safe_updates["updated_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    if _live_servicenow_enabled():
        try:
            lookup = _live_table_request(
                "incident",
                query=f"number={incident_number}",
            )
            records = lookup if isinstance(lookup, list) else ([lookup] if lookup else [])
            if not records:
                return {"success": False, "incident_number": incident_number, "message": "Live ServiceNow incident not found."}
            sys_id = records[0].get("sys_id")
            if not sys_id:
                return {"success": False, "incident_number": incident_number, "message": "ServiceNow lookup returned no sys_id."}
            payload = {}
            if "state" in safe_updates:
                payload["state"] = {"New": "1", "In Progress": "2", "Resolved": "6", "Closed": "7", "Escalated": "2"}.get(safe_updates["state"], safe_updates["state"])
            if "close_notes" in safe_updates:
                payload["close_notes"] = safe_updates["close_notes"]
            if "assignment_group" in safe_updates:
                # ServiceNow expects a group sys_id, not an arbitrary group display name.
                group = _live_table_request(
                    "sys_user_group",
                    query=f"name={safe_updates['assignment_group']}",
                )
                groups = group if isinstance(group, list) else ([group] if group else [])
                if groups and groups[0].get("sys_id"):
                    payload["assignment_group"] = groups[0]["sys_id"]
            result = _live_table_request("incident", method="PATCH", payload=payload, sys_id=sys_id)
            return {
                "success": True,
                "mode": "Live ServiceNow Instance",
                "incident_number": incident_number,
                "updated_fields": list(payload.keys()),
                "status": "Updated",
                "incident": result,
            }
        except Exception as exc:
            logger.warning("Live ServiceNow incident update failed: %s", exc)
            return {"success": False, "mode": "Live ServiceNow Instance", "incident_number": incident_number, "message": str(exc)}

    collection = get_servicenow_collection()
    result = collection.update_one(
        {"incident_number": incident_number},
        {"$set": safe_updates},
    )
    matched_count = (
        result.get("matched_count", result.get("modified_count", 0))
        if isinstance(result, dict)
        else getattr(result, "matched_count", 0)
    )
    if not matched_count:
        return {"success": False, "incident_number": incident_number, "message": f"Mock incident {incident_number} not found."}
    return {
        "success": True,
        "mode": "ServiceNow Mock REST API",
        "incident_number": incident_number,
        "updated_fields": list(safe_updates.keys()),
        "status": "Updated",
        "message": f"ServiceNow mock incident {incident_number} updated successfully."
    }


def get_servicenow_incident(incident_number: str) -> dict:
    """Retrieve an incident from the configured live API or local mock."""
    if _live_servicenow_enabled():
        try:
            result = _live_table_request("incident", query=f"number={incident_number}")
            records = result if isinstance(result, list) else ([result] if result else [])
            if records:
                return {"success": True, "mode": "Live ServiceNow Instance", "incident": records[0]}
            return {"success": False, "message": f"Incident {incident_number} not found"}
        except Exception as exc:
            logger.warning("Live ServiceNow incident retrieval failed: %s", exc)
            return {"success": False, "mode": "Live ServiceNow Instance", "message": str(exc)}

    collection = get_servicenow_collection()
    record = collection.find_one({"incident_number": incident_number}, {"_id": 0})
    if record:
        return {"success": True, "mode": "ServiceNow Mock REST API", "incident": record}
    return {"success": False, "message": f"Incident {incident_number} not found"}


def create_servicenow_service_request(request_data: dict) -> dict:
    """Create a live ServiceNow request when configured, otherwise use the mock."""
    if _live_servicenow_enabled():
        try:
            payload = {
                "short_description": f"Software Provisioning: {request_data.get('software')}",
                "description": f"Software requested: {request_data.get('software')}. Source request: {request_data.get('request_id', 'not specified')}",
                "requested_for": request_data.get("requested_for"),
            }
            payload = {key: value for key, value in payload.items() if value}
            result = _live_table_request("sc_request", method="POST", payload=payload)
            return {
                "success": True,
                "mode": "Live ServiceNow Instance",
                "request_number": result.get("number") or request_data.get("request_id"),
                "sys_id": result.get("sys_id"),
                "software": request_data.get("software"),
                "status": "Created",
                "message": "ServiceNow request created successfully."
            }
        except Exception as exc:
            logger.warning("Live ServiceNow request creation failed: %s", exc)
            return {"success": False, "mode": "Live ServiceNow Instance", "message": str(exc)}

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
