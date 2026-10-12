import os
import logging
from app.config import settings

logger = logging.getLogger(__name__)

def generate_ai_response(
    message: str,
    analysis: dict,
    knowledge_base: dict | None
) -> dict:
    """
    Generate grounded response adhering to AI Safety & Governance:
    - Grounded in approved Knowledge Base
    - Anti-hallucination safeguard for unsupported queries
    - Clear source attribution
    """
    article = knowledge_base.get("article", {}) if knowledge_base else {}
    has_kb = bool(article and article.get("content"))
    is_out_of_scope = analysis.get("category") == "Out of Scope" or analysis.get("should_escalate") and not has_kb

    # Anti-hallucination check: If no relevant KB is found for an inquiry
    if not has_kb or is_out_of_scope:
        grounded_text = (
            "⚠️ Information Unavailable in Approved Knowledge Base.\n\n"
            "Our AI Governance policies prevent generating unverified guidance for requests outside verified enterprise documentation. "
            "This inquiry has been flagged for human IT support escalation. A ticket can be created in ServiceNow for manual review."
        )
        return {
            "text": grounded_text,
            "grounded": False,
            "source_used": None,
            "model_used": "AI Safety & Governance Policy Guard"
        }

    # Try Hugging Face open-source LLM if token is present
    if settings.HF_TOKEN:
        try:
            from huggingface_hub import InferenceClient
            client = InferenceClient(api_key=settings.HF_TOKEN)
            system_prompt = (
                "You are an enterprise IT Helpdesk AI Assistant. "
                "Base your response ONLY on the provided Knowledge Base snippet. "
                "Do not hallucinate external policies or URLs. "
                "Be polite, clear, and actionable."
            )
            user_prompt = (
                f"Knowledge Base Article: '{article.get('title')}'\n"
                f"Content: {article.get('content')}\n\n"
                f"Employee Question: {message}\n"
                f"Provide a helpful step-by-step resolution based only on this article:"
            )
            resp = client.text_generation(
                prompt=f"<|system|>\n{system_prompt}\n<|user|>\n{user_prompt}\n<|assistant|>",
                model=settings.HF_LLM_MODEL,
                max_new_tokens=220,
                temperature=0.2
            )
            if resp and len(resp.strip()) > 20:
                return {
                    "text": resp.strip(),
                    "grounded": True,
                    "source_used": article.get("title"),
                    "source_id": article.get("id"),
                    "model_used": f"Hugging Face ({settings.HF_LLM_MODEL})"
                }
        except Exception as e:
            logger.info(f"Hugging Face LLM generation note: {e}")

    # High-quality deterministic grounded response
    title = article.get("title", "IT Troubleshooting Guide")
    content = article.get("content", "")
    kb_id = article.get("id", "KB-REF")

    grounded_text = (
        f"Based on enterprise documentation **{title}** ({kb_id}):\n\n"
        f"{content}\n\n"
        f"💡 **Suggested Next Step**: {analysis.get('suggested_resolution')}"
    )

    return {
        "text": grounded_text,
        "grounded": True,
        "source_used": title,
        "source_id": kb_id,
        "model_used": "Grounded Knowledge Retrieval Engine"
    }
