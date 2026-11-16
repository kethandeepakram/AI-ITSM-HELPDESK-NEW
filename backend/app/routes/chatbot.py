import logging
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel

from app.database.mongodb import get_chat_history_collection
from app.services.ai_service import analyze_ticket
from app.services.rag_service import search_knowledge_base
from app.services.llm_service import generate_ai_response

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/chat",
    tags=["AI Chatbot"]
)


class ChatRequest(BaseModel):
    message: str


@router.post("")
def chat(request: ChatRequest):
    # 1. AI intent detection, classification and safety check.
    analysis = analyze_ticket(request.message)

    # 2. RAG semantic knowledge search.
    knowledge_results = search_knowledge_base(request.message, top_k=3)
    top_article = knowledge_results[0] if knowledge_results else None

    # 3. Grounded response generation or explicit fallback.
    llm_output = generate_ai_response(
        message=request.message,
        analysis=analysis,
        knowledge_base=top_article,
    )

    result = {
        "message": request.message,
        "ai_response": llm_output["text"],
        "grounded": llm_output["grounded"],
        "ai_model": llm_output["model_used"],
        "source_used": llm_output["source_used"],
        "sources": knowledge_results,
        "knowledge_base": top_article,
        "intent": analysis["intent"],
        "category": analysis["category"],
        "subcategory": analysis["subcategory"],
        "priority": analysis["priority"],
        "impact": analysis.get("impact", "Individual"),
        "urgency": analysis["urgency"],
        "assignment_group": analysis["assignment_group"],
        "summary": analysis["summary"],
        "suggested_action": analysis["suggested_action"],
        "suggested_resolution": analysis.get("suggested_resolution"),
        "confidence_score": analysis.get("confidence_score", 0.9),
        "should_escalate": analysis.get("should_escalate", False),
        "automation_possible": analysis.get("automation_possible", False),
        "automation_action": analysis.get("automation_action"),
        "software_name": analysis.get("software_name"),
    }

    # Persist chat history as required by the assessment. If storage is unavailable,
    # don't block the employee's immediate response.
    try:
        get_chat_history_collection().insert_one({
            "chat_id": f"CHAT-{uuid4().hex[:12].upper()}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "user_message": request.message,
            "ai_response": llm_output["text"],
            "grounded": llm_output["grounded"],
            "model_used": llm_output["model_used"],
            "source_used": llm_output.get("source_used"),
            "intent": analysis.get("intent"),
            "category": analysis.get("category"),
            "priority": analysis.get("priority"),
            "confidence_score": analysis.get("confidence_score", 0.9),
            "should_escalate": analysis.get("should_escalate", False),
        })
    except Exception as exc:
        logger.warning("Chat history could not be persisted; returning response: %s", exc)

    return result
