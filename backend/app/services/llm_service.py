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
    try:
        retrieval_score = float(knowledge_base.get("score", 0.0)) if knowledge_base else 0.0
    except (TypeError, ValueError):
        retrieval_score = 0.0
    has_kb = bool(article and article.get("content") and retrieval_score >= 0.22)

    is_critical = (
        analysis.get("priority") == "P1"
        or analysis.get("impact") == "Multiple Users"
    )
    is_out_of_scope = analysis.get("category") == "Out of Scope"
    must_escalate = bool(analysis.get("should_escalate")) or is_critical or is_out_of_scope

    # Escalation and critical-incident policy takes precedence over retrieved
    # text. Never answer a P1 incident using an unrelated KB article.
    if must_escalate or not has_kb:
        if is_critical:
            grounded_text = (
                "🚨 Critical production incident detected. This request requires "
                "immediate human infrastructure support. Automated remediation is "
                "disabled for this incident; follow the organization's incident "
                "response process and keep affected stakeholders informed."
            )
        elif is_out_of_scope:
            grounded_text = (
                "⚠️ This request is outside the supported IT helpdesk scope. "
                "The approved knowledge base will not be used to invent an answer. "
                "Please contact the appropriate service desk for assistance."
            )
        elif must_escalate:
            grounded_text = (
                "⚠️ This request requires human IT support review. Automated "
                "instructions and self-healing have been withheld because the "
                "request is marked for escalation."
            )
        else:
            grounded_text = (
                "⚠️ No sufficiently relevant article was found in the approved "
                "knowledge base. To avoid providing unrelated troubleshooting steps, "
                "please contact the IT Service Desk for manual assistance."
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
