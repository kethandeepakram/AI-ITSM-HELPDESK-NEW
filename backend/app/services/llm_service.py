import logging
import requests

from app.config import settings

logger = logging.getLogger(__name__)


def _ollama_chat(system_prompt: str, user_prompt: str) -> str | None:
    """Call a locally running Ollama server. Return None when it is unavailable."""
    url = f"{settings.OLLAMA_BASE_URL}/api/chat"
    try:
        response = requests.post(
            url,
            json={
                "model": settings.OLLAMA_LLM_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
                "options": {"temperature": 0.2, "num_predict": 220},
            },
            timeout=settings.OLLAMA_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        message = data.get("message", {})
        text = message.get("content") if isinstance(message, dict) else None
        return text.strip() if isinstance(text, str) and len(text.strip()) > 20 else None
    except (requests.RequestException, ValueError, TypeError) as exc:
        logger.warning("Ollama local inference unavailable; using knowledge fallback: %s", exc)
        return None


def generate_ai_response(
    message: str,
    analysis: dict,
    knowledge_base: dict | None
) -> dict:
    """
    Generate a grounded helpdesk response.
    Safety: critical/out-of-scope cases and weak retrieval never go to an LLM.
    The approved knowledge article remains the only source of troubleshooting facts.
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

    # Escalation takes precedence: never let an LLM answer a critical incident
    # using a potentially unrelated article.
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

    system_prompt = (
        "You are an enterprise IT Helpdesk AI Assistant. Base your response ONLY "
        "on the provided approved Knowledge Base snippet. Do not invent policies, "
        "commands, or URLs. If the article does not answer the question, say so. "
        "Be polite, clear, and actionable."
    )
    user_prompt = (
        f"Knowledge Base Article: '{article.get('title')}'\n"
        f"Knowledge Base Content: {article.get('content')}\n\n"
        f"Employee Question: {message}\n"
        "Provide a helpful, concise step-by-step resolution based only on this article."
    )

    # Prefer local Ollama so this path needs no hosted inference credits.
    if settings.LLM_PROVIDER == "ollama":
        response_text = _ollama_chat(system_prompt, user_prompt)
        if response_text:
            return {
                "text": response_text,
                "grounded": True,
                "source_used": article.get("title"),
                "source_id": article.get("id"),
                "model_used": f"Ollama local ({settings.OLLAMA_LLM_MODEL})",
            }

    # Optional Hugging Face hosted inference, only when explicitly selected.
    elif settings.LLM_PROVIDER == "huggingface" and settings.HF_TOKEN:
        try:
            from huggingface_hub import InferenceClient
            client = InferenceClient(api_key=settings.HF_TOKEN)
            completion = client.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                model=settings.HF_LLM_MODEL,
                max_tokens=220,
                temperature=0.2,
            )
            response_text = completion.choices[0].message.content
            if isinstance(response_text, str) and len(response_text.strip()) > 20:
                return {
                    "text": response_text.strip(),
                    "grounded": True,
                    "source_used": article.get("title"),
                    "source_id": article.get("id"),
                    "model_used": f"Hugging Face ({settings.HF_LLM_MODEL})",
                }
        except Exception as exc:
            logger.warning("Hugging Face inference failed; using knowledge fallback: %s", exc)

    # Deterministic knowledge fallback remains available when Ollama is not
    # installed/running, the model is absent, or any external call fails.
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
        "model_used": "Grounded Knowledge Retrieval Engine",
    }
