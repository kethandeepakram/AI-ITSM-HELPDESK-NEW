import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from fastapi.testclient import TestClient
from app.main import app
from app.database.mongodb import LocalDatabase
from app.services.ai_service import _rule_based_classification
from app.services.llm_service import generate_ai_response
from app.services import llm_service
from app.services import rag_service
from app.services import automation_service
from seed_knowledge import KNOWLEDGE_ARTICLES

client = TestClient(app)


def test_local_database_cursor_and_upsert():
    db = LocalDatabase()
    collection = db["events"]
    collection.insert_one({"event_id": "old", "created_at": "2026-01-01"})
    collection.insert_one({"event_id": "new", "created_at": "2026-02-01"})

    latest = list(collection.find({}, {"_id": 0}).sort("created_at", -1).limit(1))
    assert len(latest) == 1
    assert latest[0]["event_id"] == "new"

    result = collection.update_one(
        {"id": "KB-test"},
        {"$set": {"title": "Test article"}},
        upsert=True,
    )
    assert result["upserted_id"] is not None
    assert collection.find_one({"id": "KB-test"})["title"] == "Test article"



def test_rag_chunking_and_lexical_fallback(monkeypatch):
    chunks = rag_service.chunk_text(" ".join(f"word{i}" for i in range(250)), chunk_words=80, overlap_words=10)
    assert len(chunks) >= 3
    assert all(chunk.strip() for chunk in chunks)

    monkeypatch.setattr(rag_service, "_local_model", "fallback")
    monkeypatch.setattr(rag_service, "_load_articles", lambda: KNOWLEDGE_ARTICLES)
    results = rag_service.search_knowledge_base(
        "How do I troubleshoot Outlook synchronization?",
        top_k=3,
    )

    assert results, "Lexical fallback should retrieve a relevant knowledge article"
    assert "Outlook" in results[0]["article"]["title"]
    assert results[0]["score"] >= 0.22
    assert results[0]["article"]["content"]


def test_chroma_vector_search_with_fake_store(monkeypatch):
    class FakeEmbeddingModel:
        def _embed(self, text):
            lowered = str(text).lower()
            return [1.0, 0.0] if "outlook" in lowered or "synchronization" in lowered else [0.0, 1.0]

        def encode(self, values, normalize_embeddings=True, show_progress_bar=False):
            if isinstance(values, str):
                return rag_service.np.asarray(self._embed(values), dtype=float)
            return rag_service.np.asarray([self._embed(value) for value in values], dtype=float)

    class FakeChromaCollection:
        def __init__(self):
            self.records = {}
            self.upsert_calls = 0
            self.query_calls = 0

        def upsert(self, ids, documents, metadatas, embeddings):
            self.upsert_calls += 1
            for item_id, document, metadata, embedding in zip(ids, documents, metadatas, embeddings):
                self.records[item_id] = {
                    "document": document,
                    "metadata": metadata,
                    "embedding": embedding,
                }

        def get(self, include=None):
            return {"ids": list(self.records.keys()), "metadatas": [item["metadata"] for item in self.records.values()]}

        def delete(self, ids):
            for item_id in ids:
                self.records.pop(item_id, None)

        def query(self, query_embeddings, n_results, include):
            self.query_calls += 1
            query_vector = query_embeddings[0]
            ranked = []
            for item_id, record in self.records.items():
                vector = record["embedding"]
                similarity = sum(a * b for a, b in zip(query_vector, vector))
                ranked.append((similarity, item_id, record))
            ranked.sort(key=lambda item: item[0], reverse=True)
            ranked = ranked[:n_results]
            return {
                "ids": [[item_id for _, item_id, _ in ranked]],
                "documents": [[record["document"] for _, _, record in ranked]],
                "metadatas": [[record["metadata"] for _, _, record in ranked]],
                "distances": [[1.0 - similarity for similarity, _, _ in ranked]],
            }

    fake_model = FakeEmbeddingModel()
    fake_collection = FakeChromaCollection()
    monkeypatch.setattr(rag_service, "_get_embedding_model", lambda: fake_model)
    monkeypatch.setattr(rag_service, "_load_articles", lambda: KNOWLEDGE_ARTICLES)
    monkeypatch.setattr(rag_service, "_get_chroma_collection", lambda: fake_collection)
    monkeypatch.setattr(rag_service, "_vector_index_signature", None)

    results = rag_service.search_knowledge_base(
        "How do I troubleshoot Outlook synchronization?",
        top_k=3,
    )

    assert fake_collection.upsert_calls == 1
    assert fake_collection.query_calls == 1
    assert results, "Chroma retrieval should return a relevant article"
    assert "Outlook" in results[0]["article"]["title"]
    assert results[0]["semantic_score"] > 0.9





def test_huggingface_hosted_chat_completion_path(monkeypatch):
    from types import SimpleNamespace
    import huggingface_hub

    class FakeInferenceClient:
        def __init__(self, api_key=None):
            assert api_key == "test-token"

        def chat_completion(self, messages, model, max_tokens, temperature):
            assert model == "Qwen/Qwen2.5-0.5B-Instruct"
            assert len(messages) == 2
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content="Check Outlook connection status, then run Send/Receive."
                        )
                    )
                ]
            )

    monkeypatch.setattr(llm_service.settings, "LLM_PROVIDER", "huggingface_api")
    monkeypatch.setattr(llm_service.settings, "HF_TOKEN", "test-token")
    monkeypatch.setattr(
        llm_service.settings, "HF_LLM_MODEL", "Qwen/Qwen2.5-0.5B-Instruct"
    )
    monkeypatch.setattr(huggingface_hub, "InferenceClient", FakeInferenceClient)

    output = generate_ai_response(
        message="How do I troubleshoot Outlook synchronization?",
        analysis={
            "priority": "P3",
            "impact": "Individual",
            "category": "Software",
            "suggested_resolution": "Check Outlook connectivity.",
        },
        knowledge_base={
            "article": {
                "id": "KB1003",
                "title": "Outlook Synchronization",
                "content": "Check Outlook connectivity and Send/Receive.",
            },
            "score": 0.8,
        },
    )

    assert output["grounded"] is True
    assert output["model_used"] == "Hugging Face Inference Providers (Qwen/Qwen2.5-0.5B-Instruct)"
    assert "Check Outlook connection status" in output["text"]
    assert output["source_id"] == "KB1003"


def test_local_transformers_chat_response_path(monkeypatch):
    monkeypatch.setattr(llm_service.settings, "LLM_PROVIDER", "transformers")
    monkeypatch.setattr(
        llm_service.settings, "HF_LLM_MODEL", "Qwen/Qwen2.5-0.5B-Instruct"
    )
    monkeypatch.setattr(
        llm_service,
        "_generate_with_transformers",
        lambda messages, max_new_tokens, temperature:
            "Open Outlook, select Send/Receive, and check account connectivity.",
    )

    output = generate_ai_response(
        message="How do I troubleshoot Outlook synchronization?",
        analysis={
            "priority": "P3",
            "impact": "Individual",
            "category": "Software",
            "suggested_resolution": "Check Outlook connectivity.",
        },
        knowledge_base={
            "article": {
                "id": "KB1003",
                "title": "Outlook Synchronization",
                "content": "Check Outlook connectivity and Send/Receive.",
            },
            "score": 0.8,
        },
    )

    assert output["grounded"] is True
    assert output["model_used"] == "Hugging Face Transformers local (Qwen/Qwen2.5-0.5B-Instruct)"
    assert "Send/Receive" in output["text"]
    assert output["source_id"] == "KB1003"


def test_transformers_unavailable_uses_grounded_fallback(monkeypatch):
    monkeypatch.setattr(llm_service.settings, "LLM_PROVIDER", "transformers")
    monkeypatch.setattr(
        llm_service,
        "_generate_with_transformers",
        lambda messages, max_new_tokens, temperature: None,
    )
    output = generate_ai_response(
        message="How do I troubleshoot Outlook synchronization?",
        analysis={
            "priority": "P3",
            "impact": "Individual",
            "category": "Software",
            "suggested_resolution": "Check Outlook connectivity.",
        },
        knowledge_base={
            "article": {
                "id": "KB1003",
                "title": "Outlook Synchronization",
                "content": "Check Outlook connectivity and Send/Receive.",
            },
            "score": 0.8,
        },
    )
    assert output["grounded"] is True
    assert output["model_used"] == "Grounded Knowledge Retrieval Engine"
    assert "Outlook Synchronization" in output["text"]



def test_malformed_generated_steps_fall_back_to_knowledge_article(monkeypatch):
    from app.services.llm_service import _clean_generated_response

    malformed = (
        "To troubleshoot Outlook synchronization issues:\n\n"
        "1. **Check Internet Connection**: Ensure you have a stable internet connection.\n"
        "2. **Verify VPN Connection**: If using a VPN, make sure it works properly.\n"
        "3."
    )
    assert _clean_generated_response(malformed) is None

    monkeypatch.setattr(llm_service.settings, "LLM_PROVIDER", "transformers")
    monkeypatch.setattr(llm_service.settings, "HF_LLM_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")
    monkeypatch.setattr(
        llm_service,
        "_generate_with_transformers",
        lambda messages, max_new_tokens, temperature: malformed,
    )

    output = generate_ai_response(
        message="How do I troubleshoot Outlook synchronization?",
        analysis={
            "priority": "P3",
            "impact": "Individual",
            "category": "Software",
            "suggested_resolution": "Check Outlook synchronization settings.",
        },
        knowledge_base={
            "article": {
                "id": "KB1003",
                "title": "Microsoft Outlook Mailbox Synchronization Troubleshooting",
                "content": (
                    "To resolve Outlook email synchronization issues:\n"
                    "1. Check the Outlook status bar for Disconnected or Trying to connect.\n"
                    "2. Use Send/Receive All Folders or press F9.\n"
                    "3. Verify Cached Exchange Mode is enabled.\n"
                    "4. Rebuild the local OST cache only if earlier steps fail."
                ),
            },
            "score": 0.8,
        },
    )

    assert output["model_used"] == "Grounded Knowledge Retrieval Engine"
    assert "Cached Exchange Mode" in output["text"]
    assert "Send/Receive All Folders" in output["text"]
    assert "\n3.\n" not in output["text"]


def test_transformers_ticket_classification_refinement(monkeypatch):
    from app.services import ai_service

    monkeypatch.setattr(ai_service.settings, "LLM_PROVIDER", "transformers")
    monkeypatch.setattr(ai_service.settings, "HF_REFINE_TICKET_TEXT", True)
    monkeypatch.setattr(
        ai_service,
        "generate_llm_text",
        lambda messages, max_new_tokens, temperature:
            '{"summary":"Outlook login issue",'
            '"suggested_resolution":"Check the account and connectivity.",'
            '"confidence_score":0.91}',
    )
    result = ai_service.analyze_ticket(
        "I need help because Outlook keeps failing to connect"
    )
    assert result["summary"] == "Outlook login issue"
    assert result["suggested_resolution"] == "Check the account and connectivity."
    # Deterministic category and workflow fields remain authoritative.
    assert result["category"] == "Software"
    assert result["automation_action"] == "cache_clear"



def test_ticket_classification_skips_second_llm_call_by_default(monkeypatch):
    from app.services import ai_service

    monkeypatch.setattr(ai_service.settings, "LLM_PROVIDER", "transformers")
    monkeypatch.setattr(ai_service.settings, "HF_REFINE_TICKET_TEXT", False)

    def unexpected_llm_call(*args, **kwargs):
        raise AssertionError("classification should not make a second local-model call")

    monkeypatch.setattr(ai_service, "generate_llm_text", unexpected_llm_call)
    result = ai_service.analyze_ticket(
        "How do I troubleshoot Outlook synchronization?"
    )
    assert result["category"] == "Software"
    assert result["subcategory"] == "Email / Outlook"
    assert result["automation_action"] == "cache_clear"


def test_chat_endpoint_returns_response_and_persists_history(monkeypatch):
    from app.routes import chatbot

    stored = []

    class FakeCollection:
        def insert_one(self, document):
            stored.append(document)

    fake_analysis = {
        "intent": "Knowledge Question",
        "category": "Software",
        "subcategory": "Email / Outlook",
        "priority": "P3",
        "impact": "Individual",
        "urgency": "Medium",
        "assignment_group": "Application Support",
        "summary": "Outlook synchronization question",
        "suggested_action": "Check Outlook connectivity.",
        "suggested_resolution": "Check Outlook connectivity.",
        "confidence_score": 0.91,
        "should_escalate": False,
        "automation_possible": False,
        "automation_action": None,
        "software_name": None,
    }
    fake_sources = [{
        "article": {
            "id": "KB1003",
            "title": "Outlook Synchronization",
            "category": "Software",
            "content": "Check Outlook connectivity and Send/Receive.",
        },
        "score": 0.8,
    }]
    fake_answer = {
        "text": "Open Outlook and check Send/Receive.",
        "grounded": True,
        "source_used": "Outlook Synchronization",
        "source_id": "KB1003",
        "model_used": "Test model",
    }

    monkeypatch.setattr(chatbot, "analyze_ticket", lambda message: fake_analysis)
    monkeypatch.setattr(chatbot, "search_knowledge_base", lambda message, top_k: fake_sources)
    monkeypatch.setattr(chatbot, "generate_ai_response", lambda **kwargs: fake_answer)
    monkeypatch.setattr(chatbot, "get_chat_history_collection", lambda: FakeCollection())

    response = client.post(
        "/api/chat",
        json={"message": "How do I troubleshoot Outlook synchronization?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ai_response"] == fake_answer["text"]
    assert data["source_used"] == "Outlook Synchronization"
    assert data["confidence_score"] == 0.91
    assert len(stored) == 1
    assert stored[0]["user_message"] == "How do I troubleshoot Outlook synchronization?"
    assert stored[0]["source_used"] == "Outlook Synchronization"
    assert stored[0]["chat_id"].startswith("CHAT-")



def test_simulated_software_provisioning_status_is_consistent(monkeypatch):
    db = LocalDatabase()
    provisioning = db["software_provisioning"]
    audit_entries = []

    monkeypatch.setattr(
        automation_service,
        "get_provisioning_collection",
        lambda: provisioning,
    )
    monkeypatch.setattr(
        automation_service,
        "log_audit_trail",
        lambda **entry: audit_entries.append(entry) or entry,
    )

    result = automation_service.execute_automation(
        action="software_install",
        ticket_id="TEST-PROVISIONING-STATUS",
        software_name="Visual Studio Code",
    )
    record = provisioning.find_one(
        {"ticket_id": "TEST-PROVISIONING-STATUS"}
    )

    assert result["success"] is True
    assert result["mode"] == "SIMULATED"
    assert result["status"] == "Completed (Simulated)"
    assert "no endpoint software was installed" in result["message"].lower()
    assert record["status"] == "Completed (Simulated)"
    assert record["execution_mode"] == "SIMULATED"
    assert record["software_installed"] is False
    assert record["servicenow_status"] == "Mock request created; no software installed"
    assert any(entry.get("status") == "Simulated" for entry in audit_entries)

def test_rule_based_safety_and_intent_guards():
    outage = _rule_based_classification(
        "The production server is down and multiple employees cannot access the application"
    )
    assert outage["priority"] == "P1"
    assert outage["should_escalate"] is True
    assert outage["automation_possible"] is False
    assert outage["automation_action"] is None
    assert outage["assignment_group"] == "Infrastructure / L2 Support"

    # A highly scored but unrelated article must never replace critical-incident handling.
    response = generate_ai_response(
        "The production server is down and multiple employees cannot access the application",
        outage,
        {
            "article": {
                "title": "Software Installation Request",
                "content": "Install the approved software from the catalog."
            },
            "score": 0.99,
        },
    )
    assert response["grounded"] is False
    assert "Critical production incident" in response["text"]
    assert "Install the approved software" not in response["text"]

    install = _rule_based_classification("Please install Microsoft Teams on my laptop")
    assert install["subcategory"] == "Software Provisioning"
    assert install["automation_action"] == "software_install"

    app_problem = _rule_based_classification("Python keeps crashing when I open my project")
    assert app_problem["subcategory"] != "Software Provisioning"
    assert app_problem["automation_action"] != "software_install"

def test_all_scenarios():
    test_local_database_cursor_and_upsert()
    test_rule_based_safety_and_intent_guards()
    print("=================================================================")
    print("RUNNING 5 MANDATORY HACKATHON LIVE DEMO SCENARIOS")
    print("=================================================================\n")

    # 1. Scenario 1: Intelligent Ticket Intake
    print("--- SCENARIO 1: Intelligent Ticket Intake ---")
    r1 = client.post("/api/demo/run/1")
    assert r1.status_code == 200, f"Scenario 1 failed: {r1.text}"
    d1 = r1.json()
    assert d1["expected_ai_output"]["category_subcategory"] == "Network / VPN"
    assert d1["expected_ai_output"]["priority"] == "P2"
    assert d1["servicenow_incident"]["success"] is True
    print(f"Prompt: {d1['prompt']}")
    print(f"Expected AI Output:")
    for k, v in d1['expected_ai_output'].items():
        print(f"  {k}: {v}")
    print(f"ServiceNow Incident Created: {d1['servicenow_incident']['incident_number']}")
    print("-> SCENARIO 1 PASSED!\n")

    # 2. Scenario 2: Self-Healing
    print("--- SCENARIO 2: Self-Healing Agent ---")
    r2 = client.post("/api/demo/run/2")
    assert r2.status_code == 200, f"Scenario 2 failed: {r2.text}"
    d2 = r2.json()
    assert d2["ticket"]["status"] == "Resolved"
    assert d2["ticket"].get("automation_status") == "Success"
    assert d2["automation_result"]["success"] is True
    assert d2["automation_result"]["mode"] == "SIMULATED"
    print(f"Prompt: {d2['prompt']}")
    print("Workflow executed:")
    for step in d2['workflow_executed']:
        print(f"  {step}")
    print(f"Action Status: {d2['status']}")
    print(f"ServiceNow Incident Number: {d2['ticket'].get('servicenow_incident')}")
    print("-> SCENARIO 2 PASSED!\n")

    # 3. Scenario 3: RAG
    print("--- SCENARIO 3: Knowledge Management Automation (RAG) ---")
    r3 = client.post("/api/demo/run/3")
    assert r3.status_code == 200, f"Scenario 3 failed: {r3.text}"
    d3 = r3.json()
    assert d3["sources_attributed"], "RAG should return a relevant Outlook source"
    assert d3["analysis"]["subcategory"] == "Email / Outlook"
    assert "Outlook" in d3["sources_attributed"][0]["title"]
    assert d3["grounded_llm_response"].strip()
    print(f"Prompt: {d3['prompt']}")
    print("Retrieved Sources:")
    for s in d3['sources_attributed']:
        print(f"  - {s['title']} (Score: {s['score']})")
    print(f"Grounded Response Preview:\n{d3['grounded_llm_response'][:200]}...")
    print("-> SCENARIO 3 PASSED!\n")

    # 4. Scenario 4: Software Provisioning
    print("--- SCENARIO 4: Software Provisioning Automation ---")
    r4 = client.post("/api/demo/run/4")
    assert r4.status_code == 200, f"Scenario 4 failed: {r4.text}"
    d4 = r4.json()
    assert d4["ui_result"]["software"] == "Visual Studio Code"
    assert d4["ui_result"]["status"] == "Completed (Simulated)"
    assert d4["status"] == "Completed (Simulated)"
    assert d4["ui_result"]["servicenow"] == "Mock request created; no software installed"
    assert d4["servicenow_details"]["success"] is True
    assert d4["provisioning_workflow"], "Provisioning workflow steps should be returned"
    print(f"Prompt: {d4['prompt']}")
    print(f"UI Result:")
    for k, v in d4['ui_result'].items():
        print(f"  {k}: {v}")
    print("Workflow:")
    for step in d4['provisioning_workflow']:
        print(f"  {step}")
    print("-> SCENARIO 4 PASSED!\n")

    # 5. Scenario 5: Unknown Question & AI Safety
    print("--- SCENARIO 5: AI Safety, Governance & Escalation ---")
    r5 = client.post("/api/demo/run/5")
    assert r5.status_code == 200, f"Scenario 5 failed: {r5.text}"
    d5 = r5.json()
    assert d5["analysis"]["category"] == "Out of Scope"
    assert d5["confidence_score"] < 0.65
    assert d5["escalation_required"] is True
    assert d5["is_grounded"] is False
    assert d5["ticket"]["status"] == "Escalated"
    assert d5["servicenow_incident"]["success"] is True
    print(f"Prompt: {d5['prompt']}")
    print(f"Confidence Score: {d5['confidence_score']} (Below threshold)")
    print(f"Grounded in KB: {d5['is_grounded']}")
    print(f"Hallucination Guard: {d5['no_hallucination_guard']}")
    print(f"Escalation Required: {d5['escalation_required']}")
    print(f"Response: {d5['ai_response'][:180]}...")
    print("-> SCENARIO 5 PASSED!\n")

    print("=================================================================")
    print("ALL 5 HACKATHON SCENARIOS TESTED AND PASSED WITH 100% SUCCESS!")
    print("=================================================================")

if __name__ == "__main__":
    test_all_scenarios()
