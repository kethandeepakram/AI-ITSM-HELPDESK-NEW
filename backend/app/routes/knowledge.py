from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.database.mongodb import get_knowledge_collection
from app.services.rag_service import search_knowledge_base
from seed_knowledge import KNOWLEDGE_ARTICLES, seed_knowledge_base

router = APIRouter(
    prefix="/api/knowledge",
    tags=["Knowledge Base & RAG"]
)

class KnowledgeSearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3

@router.get("")
def get_knowledge_articles():
    try:
        collection = get_knowledge_collection()
        articles = list(collection.find({}, {"_id": 0}))
        if not articles:
            articles = KNOWLEDGE_ARTICLES

        return {
            "success": True,
            "count": len(articles),
            "articles": articles
        }
    except Exception as e:
        return {
            "success": False,
            "articles": KNOWLEDGE_ARTICLES,
            "error": str(e)
        }

@router.post("/search")
def search_knowledge(request: KnowledgeSearchRequest):
    results = search_knowledge_base(request.query, top_k=request.top_k or 3)
    return {
        "success": True,
        "query": request.query,
        "count": len(results),
        "results": results
    }

@router.post("/seed")
def seed_kb():
    seed_knowledge_base()
    return {"success": True, "message": "Knowledge base seeded with 7 official IT articles"}