from fastapi import APIRouter
from app.database.mongodb import get_audit_collection

router = APIRouter(
    prefix="/api/audit",
    tags=["Audit Logs"]
)

@router.get("/logs")
def get_audit_logs():
    collection = get_audit_collection()
    logs = list(collection.find({}, {"_id": 0}).sort("timestamp", -1))
    return {
        "success": True,
        "count": len(logs),
        "logs": logs
    }
