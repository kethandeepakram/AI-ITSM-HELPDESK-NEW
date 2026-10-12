import os
import re
import json
import logging
import requests
from app.config import settings

logger = logging.getLogger(__name__)

# Software catalog keywords for intent routing
SOFTWARE_LIST = [
    "visual studio code", "vs code", "microsoft teams", "teams", "python",
    "java", "node.js", "docker", "git", "google chrome", "chrome",
    "postman", "intellij idea", "intellij", "eclipse", "zoom", "slack"
]

def _rule_based_classification(message: str) -> dict:
    """High-accuracy enterprise IT intent & entity extraction."""
    text = message.lower().strip()

    intent = "Incident"
    category = "General IT"
    subcategory = "General Support"
    priority = "P3"
    impact = "Individual"
    urgency = "Medium"
    assignment_group = "IT Service Desk"
    summary = message[:60] + ("..." if len(message) > 60 else "")
    suggested_resolution = "Investigate IT issue and follow standard operating procedures."
    automation_possible = False
    automation_action = None
    software_name = None
    confidence_score = 0.88
    should_escalate = False

    if any(k in text for k in [
        "production server is down", "production server down", "server outage",
        "production outage", "multiple employees cannot access",
        "multiple users cannot access", "application is down",
        "production application unavailable"
    ]):
        intent = "Incident"
        category = "Server"
        subcategory = "Production Outage"
        priority = "P1"
        impact = "Multiple Users"
        urgency = "High"
        assignment_group = "Infrastructure / L2 Support"
        summary = "Critical production server outage"
        suggested_resolution = (
            "Critical production outage detected. Escalate immediately "
            "to infrastructure support and investigate service availability."
        )
        automation_possible = False
        automation_action = None
        confidence_score = 0.99
        should_escalate = True

    elif "vpn" in text:
        intent = "Incident"
        category = "Network"
        subcategory = "VPN"
        priority = "P2"
        impact = "Individual"
        urgency = "High"
        assignment_group = "Network Support"
        summary = "VPN authentication failure" if ("auth" in text or "fail" in text or "connect" in text) else "VPN connection issue"
        suggested_resolution = "VPN troubleshooting: verify network connectivity, clear cache, restart VPN client."
        automation_possible = True
        automation_action = "vpn_status_check"
        confidence_score = 0.96

    elif any(k in text for k in ["password", "forgot password", "reset password", "password expired"]):
        intent = "Automatable Issue"
        category = "Account & Access"
        subcategory = "Password Reset"
        priority = "P2"
        impact = "Individual"
        urgency = "High"
        assignment_group = "Identity & Access Management"
        summary = "Expired or forgotten password self-service reset request"
        suggested_resolution = "Execute automated self-healing password reset workflow and notify user via secure channel."
        automation_possible = True
        automation_action = "password_reset"
        confidence_score = 0.98

    elif any(k in text for k in ["locked", "account locked", "unlock account"]):
        intent = "Automatable Issue"
        category = "Account & Access"
        subcategory = "Account Unlock"
        priority = "P2"
        impact = "Individual"
        urgency = "High"
        assignment_group = "Identity & Access Management"
        summary = "User account locked due to failed authentication attempts"
        suggested_resolution = "Verify identity and trigger automated account unlock self-heal action."
        automation_possible = True
        automation_action = "account_unlock"
        confidence_score = 0.97

    elif any(k in text for k in [
        "install", "installation", "installed", "installing", "provision",
        "provisioning", "software request", "request software", "need software",
        "deploy software", "set up software", "setup software"
    ]):
        intent = "Service Request"
        category = "Software"
        subcategory = "Software Provisioning"
        priority = "P3"
        impact = "Individual"
        urgency = "Medium"
        assignment_group = "IT Service Desk"
        detected_software = "Visual Studio Code"
        for sw in SOFTWARE_LIST:
            if sw in text:
                if sw in ["visual studio code", "vs code"]:
                    detected_software = "Visual Studio Code"
                elif sw in ["microsoft teams", "teams"]:
                    detected_software = "Microsoft Teams"
                elif sw in ["google chrome", "chrome"]:
                    detected_software = "Google Chrome"
                elif sw in ["intellij", "intellij idea"]:
                    detected_software = "IntelliJ IDEA"
                else:
                    detected_software = sw.capitalize()
                break
        software_name = detected_software
        summary = f"Software installation request: {software_name}"
        suggested_resolution = f"Validate {software_name} in enterprise catalogue and execute automated provisioning."
        automation_possible = True
        automation_action = "software_install"
        confidence_score = 0.95

    elif any(k in text for k in ["outlook", "synchronization", "sync", "email", "mailbox"]):
        intent = "Knowledge Question"
        category = "Software"
        subcategory = "Email / Outlook"
        priority = "P3"
        impact = "Individual"
        urgency = "Medium"
        assignment_group = "Application Support"
        summary = "Outlook mailbox synchronization / connectivity troubleshooting"
        suggested_resolution = "Run Outlook connection status check, update offline address book, and rebuild OST cache if necessary."
        automation_possible = True
        automation_action = "cache_clear"
        confidence_score = 0.93

    elif any(k in text for k in ["wifi", "wi-fi", "wireless", "ssid", "internet disconnected"]):
        intent = "Incident"
        category = "Network"
        subcategory = "WiFi"
        priority = "P2"
        impact = "Individual"
        urgency = "High"
        assignment_group = "Network Support"
        summary = "Office Wi-Fi connection failure"
        suggested_resolution = "Flush DNS, cycle wireless network adapter, re-authenticate with 802.1X certificate."
        automation_possible = True
        automation_action = "service_restart"
        confidence_score = 0.94

    elif any(k in text for k in ["slow", "laptop performance", "freeze", "cpu", "memory", "ram", "overheating"]):
        intent = "Incident"
        category = "Hardware"
        subcategory = "Laptop Performance"
        priority = "P3"
        impact = "Individual"
        urgency = "Medium"
        assignment_group = "Desktop Support"
        summary = "System performance degradation and high resource utilization"
        suggested_resolution = "Clear temporary files, analyze running background processes, inspect thermal throttling."
        automation_possible = True
        automation_action = "cache_clear"
        confidence_score = 0.91

    elif any(k in text for k in [
        "flight", "hotel", "weather", "recipe", "pizza", "movie", "paris", "joke", "sports",
        "stock", "invest", "crypto", "dating", "car", "salary", "bonus"
    ]):
        intent = "Unsupported Question"
        category = "Out of Scope"
        subcategory = "Non-IT Request"
        priority = "P4"
        impact = "Individual"
        urgency = "Low"
        assignment_group = "IT Service Desk"
        summary = f"Out-of-scope inquiry: {message[:40]}"
        suggested_resolution = "Approved IT Knowledge Base does not contain information for this non-IT topic. Human escalation recommended."
        automation_possible = False
        automation_action = None
        confidence_score = 0.32
        should_escalate = True

    elif len(text.split()) < 3 and not any(k in text for k in ["vpn", "wifi", "help"]):
        confidence_score = 0.50
        should_escalate = True
        suggested_resolution = "Insufficient details provided. Escalate to human IT technician for clarification."

    return {
        "intent": intent,
        "category": category,
        "subcategory": subcategory,
        "priority": priority,
        "impact": impact,
        "urgency": urgency,
        "assignment_group": assignment_group,
        "summary": summary,
        "suggested_action": suggested_resolution,
        "suggested_resolution": suggested_resolution,
        "automation_possible": automation_possible,
        "automation_action": automation_action,
        "software_name": software_name,
        "confidence_score": round(confidence_score, 2),
        "should_escalate": should_escalate or (confidence_score < settings.CONFIDENCE_THRESHOLD)
    }

def _ollama_classification(message: str) -> dict | None:
    """Optional local LLM refinement; deterministic workflow fields remain authoritative."""
    prompt = (
        "You are an enterprise IT helpdesk assistant. Return valid JSON with keys "
        "summary, suggested_resolution, confidence_score. Do not trigger automation. "
        "Keep the answer concise and grounded in the employee's text.\n"
        f"Employee request: {message}\nJSON:"
    )
    try:
        response = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.1, "num_predict": 250},
            },
            timeout=settings.OLLAMA_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        raw = data.get("response", "")
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        return json.loads(match.group(0)) if match else None
    except (requests.RequestException, ValueError, TypeError) as exc:
        logger.info("Ollama classification unavailable; keeping rule-based output: %s", exc)
        return None


def analyze_ticket(message: str) -> dict:
    """Analyze a request while keeping deterministic safety rules authoritative."""
    base = _rule_based_classification(message)

    # Critical incidents and mandatory escalations never pass through an LLM.
    if base.get("priority") == "P1" or base.get("should_escalate"):
        return base

    parsed = None
    if settings.LLM_PROVIDER == "ollama":
        parsed = _ollama_classification(message)
    elif settings.LLM_PROVIDER == "huggingface" and settings.HF_TOKEN:
        try:
            from huggingface_hub import InferenceClient
            client = InferenceClient(api_key=settings.HF_TOKEN)
            prompt = (
                "You are an enterprise IT Helpdesk classifier. Analyze the following employee request and respond in valid JSON only with keys:\n"
                "intent, category, subcategory, priority (P1, P2, P3, P4), impact, urgency, assignment_group, summary, suggested_resolution, automation_possible (boolean), confidence_score (float between 0 and 1).\n\n"
                f"Employee Request: \"{message}\"\n\nJSON:"
            )
            resp = client.text_generation(
                prompt=prompt,
                model=settings.HF_LLM_MODEL,
                max_new_tokens=250,
                temperature=0.1
            )
            json_match = re.search(r"\{.*\}", resp, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
        except Exception as exc:
            logger.info("Hugging Face inference unavailable; keeping rule-based output: %s", exc)

    if parsed:
        # Deterministic rules remain authoritative. The LLM can refine just
        # wording and confidence, and may only refine broad General IT labels.
        allowed_fields = ["summary", "suggested_resolution", "confidence_score"]
        if base.get("category") == "General IT":
            allowed_fields.extend([
                "intent", "category", "subcategory", "priority",
                "impact", "urgency", "assignment_group"
            ])
        for key in allowed_fields:
            value = parsed.get(key)
            if value is not None:
                base[key] = value

        base["suggested_action"] = base.get("suggested_resolution")
        try:
            model_confidence = float(base.get("confidence_score", 0.9))
        except (TypeError, ValueError):
            model_confidence = 0.9
        model_confidence = min(max(model_confidence, 0.0), 1.0)
        base["confidence_score"] = round(model_confidence, 2)
        base["should_escalate"] = bool(
            base.get("should_escalate", False)
            or model_confidence < settings.CONFIDENCE_THRESHOLD
            or base.get("priority") == "P1"
            or base.get("category") == "Out of Scope"
        )
        if base["should_escalate"]:
            base["automation_possible"] = False
            base["automation_action"] = None
            base["software_name"] = None
    return base
