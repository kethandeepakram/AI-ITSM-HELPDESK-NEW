from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai_service import analyze_ticket
from app.services.rag_service import search_knowledge_base
from app.services.llm_service import generate_ai_response

router = APIRouter(
    prefix="/api/chat",
    tags=["AI Chatbot"]
)

class ChatRequest(BaseModel):
    message: str

@router.post("")
def chat(request: ChatRequest):
    # 1. AI Intent Detection, Classification & Safety Check
    analysis = analyze_ticket(request.message)

    # 2. RAG Semantic Knowledge Search
    knowledge_results = search_knowledge_base(request.message, top_k=3)
    top_article = knowledge_results[0] if knowledge_results else None

    # 3. Grounded LLM Response with Anti-Hallucination Guard
    llm_output = generate_ai_response(
        message=request.message,
        analysis=analysis,
        knowledge_base=top_article
    )

    return {
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
        "software_name": analysis.get("software_name")
    }