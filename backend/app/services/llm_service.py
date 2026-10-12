import logging
import re
import threading

from app.config import settings

logger = logging.getLogger(__name__)

# Load the model once per backend process. Serialize local inference to reduce
# the risk of concurrent requests exhausting RAM on a development machine.
_model_lock = threading.RLock()
_cached_model_id: str | None = None
_cached_tokenizer = None
_cached_model = None


def _generate_with_transformers(
    messages: list[dict],
    max_new_tokens: int,
    temperature: float,
) -> str | None:
    """Run a public Hugging Face causal language model locally with Transformers."""
    global _cached_model_id, _cached_tokenizer, _cached_model

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        with _model_lock:
            model_id = settings.HF_LLM_MODEL
            if _cached_model is None or _cached_model_id != model_id:
                logger.info(
                    "Loading Hugging Face model %s locally; the first request may take time.",
                    model_id,
                )
                token = settings.HF_TOKEN or None
                tokenizer = AutoTokenizer.from_pretrained(
                    model_id,
                    token=token,
                    trust_remote_code=False,
                )

                # Use half precision on CUDA GPUs. CPU float32 is more portable but
                # needs several GB of RAM for the recommended 1.5B parameter model.
                if torch.cuda.is_available():
                    model = AutoModelForCausalLM.from_pretrained(
                        model_id,
                        token=token,
                        torch_dtype=torch.float16,
                        device_map="auto",
                        trust_remote_code=False,
                    )
                else:
                    model = AutoModelForCausalLM.from_pretrained(
                        model_id,
                        token=token,
                        torch_dtype=torch.float32,
                        low_cpu_mem_usage=True,
                        trust_remote_code=False,
                    )
                    model.to("cpu")

                model.eval()
                _cached_tokenizer = tokenizer
                _cached_model = model
                _cached_model_id = model_id

            tokenizer = _cached_tokenizer
            model = _cached_model

            if getattr(tokenizer, "chat_template", None):
                prompt = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                )
            else:
                prompt = "\n\n".join(
                    f"{item.get('role', 'user').upper()}: {item.get('content', '')}"
                    for item in messages
                ) + "\nASSISTANT:"

            inputs = tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048,
            )
            model_device = next(model.parameters()).device
            inputs = {key: value.to(model_device) for key, value in inputs.items()}

            generation_args = {
                "max_new_tokens": min(max(int(max_new_tokens), 1), 512),
                "do_sample": temperature > 0,
                "pad_token_id": tokenizer.eos_token_id,
            }
            if temperature > 0:
                generation_args["temperature"] = max(float(temperature), 0.05)
                generation_args["top_p"] = 0.9

            with torch.inference_mode():
                output_ids = model.generate(**inputs, **generation_args)

            prompt_length = inputs["input_ids"].shape[-1]
            answer_ids = output_ids[0][prompt_length:]
            answer = tokenizer.decode(answer_ids, skip_special_tokens=True).strip()
            return answer if len(answer) > 20 else None
    except Exception as exc:
        # Do not fail ticket intake when model download/inference is unavailable.
        logger.warning(
            "Local Hugging Face model %s unavailable; using grounded fallback. Error: %s",
            settings.HF_LLM_MODEL,
            exc,
        )
        return None


def _generate_with_huggingface_api(
    messages: list[dict],
    max_new_tokens: int,
    temperature: float,
) -> str | None:
    """Optional hosted Inference Providers route; it may require remaining credits."""
    if not settings.HF_TOKEN:
        logger.info("HF_TOKEN is empty; hosted Hugging Face inference is disabled.")
        return None

    try:
        from huggingface_hub import InferenceClient

        client = InferenceClient(api_key=settings.HF_TOKEN)
        completion = client.chat_completion(
            messages=messages,
            model=settings.HF_LLM_MODEL,
            max_tokens=min(max(int(max_new_tokens), 1), 512),
            temperature=max(float(temperature), 0.01),
        )
        text = completion.choices[0].message.content
        return text.strip() if isinstance(text, str) and len(text.strip()) > 20 else None
    except Exception as exc:
        logger.warning(
            "Hosted Hugging Face inference unavailable; using grounded fallback. Error: %s",
            exc,
        )
        return None


def generate_llm_text(
    messages: list[dict],
    max_new_tokens: int = 220,
    temperature: float = 0.2,
) -> str | None:
    """Select the configured LLM provider; no hosted inference credits are needed by default."""
    if settings.LLM_PROVIDER == "transformers":
        return _generate_with_transformers(messages, max_new_tokens, temperature)
    if settings.LLM_PROVIDER == "huggingface_api":
        return _generate_with_huggingface_api(messages, max_new_tokens, temperature)
    return None



def _clean_generated_response(response: str | None) -> str | None:
    """
    Normalize model output for the plain-text chat UI.
    Reject incomplete numbered/bulleted steps so the caller can use the
    authoritative RAG article rather than display an unfinished answer.
    """
    if not isinstance(response, str) or len(response.strip()) < 20:
        return None

    lines = []
    for raw_line in response.splitlines():
        line = raw_line.strip()

        # The React chat view displays text, not Markdown, so normalize common markers.
        line = re.sub(r"^#{1,6}\s*", "", line)
        line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
        line = re.sub(r"__(.*?)__", r"\1", line)
        line = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", line)

        # A dangling list marker means the model probably hit its token limit.
        if re.match(r"^\s*(?:\d+[.)]?|[-*•])\s*$", line):
            return None

        lines.append(line)

    # The last numbered step must end as a complete sentence. Small models often
    # stop mid-step at the token cap; prefer the full approved article in that case.
    nonempty_lines = [line for line in lines if line]
    if nonempty_lines and re.match(r"^\d+[.)]\s+\S", nonempty_lines[-1]):
        if not re.search(r"[.!?][\"'’”)}\]]*\s*$", nonempty_lines[-1]):
            return None

    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned if len(cleaned) >= 20 else None


def generate_ai_response(
    message: str,
    analysis: dict,
    knowledge_base: dict | None
) -> dict:
    """
    Generate a helpdesk response grounded in the approved RAG article.
    Critical/escalated and weak-retrieval cases never go to an LLM.
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

    # Policy guard takes precedence over generated answers.
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

    messages = [
        {
            "role": "system",
            "content": (
                "You are an enterprise IT Helpdesk assistant. Treat the supplied knowledge "
                "article as the only source of troubleshooting facts. Never invent troubleshooting "
                "steps, settings, commands, or policies. Reply in plain text using at most TWO "
                "short sentences and no numbered list, bullets, headings, or Markdown. Mention "
                "only the most relevant checks that are explicitly supported by the article. "
                "If the article does not answer the question, say that the approved article does "
                "not cover it. Do not continue with extra steps."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Approved Knowledge Base Article: '{article.get('title')}'\n"
                f"Article Content: {article.get('content')}\n\n"
                f"Employee Question: {message}\n"
                "Answer in no more than two short plain-text sentences, using only this article."
            ),
        },
    ]
    response_text = generate_llm_text(
        messages,
        max_new_tokens=settings.HF_MAX_NEW_TOKENS,
        temperature=0.1,
    )
    response_text = _clean_generated_response(response_text)
    if response_text is None:
        logger.warning(
            "Generated helpdesk answer was empty or structurally invalid; using the retrieved article."
        )

    if response_text:
        if settings.LLM_PROVIDER == "transformers":
            model_used = f"Hugging Face Transformers local ({settings.HF_LLM_MODEL})"
        else:
            model_used = f"Hugging Face Inference Providers ({settings.HF_LLM_MODEL})"
        return {
            "text": response_text,
            "grounded": True,
            "source_used": article.get("title"),
            "source_id": article.get("id"),
            "model_used": model_used,
        }

    title = article.get("title", "IT Troubleshooting Guide")
    content = str(article.get("content", "") or "").strip()
    kb_id = article.get("id", "KB-REF")
    # Display the authoritative source article as clean text, without a second
    # potentially conflicting suggestion appended from the ticket classifier.
    grounded_text = f"Source: {title} ({kb_id})\n\n{content}"
    return {
        "text": grounded_text,
        "grounded": True,
        "source_used": title,
        "source_id": kb_id,
        "model_used": "Grounded Knowledge Retrieval Engine",
    }
