# SORIM.Ai — AI-Powered ITSM Helpdesk

An AI-assisted IT service desk prototype built with **React, FastAPI, MongoDB, retrieval-augmented generation (RAG), and simulated self-healing workflows**. It demonstrates how an employee issue can be classified, linked to knowledge-base guidance, recorded as a ticket, and routed toward automation or human escalation.

> **Prototype note:** Integrations and remediation workflows may be simulated or use fallback behavior when external services are not configured. Do not use this project to perform real production changes without adding appropriate authentication, authorization, safeguards, and operational validation.

## Features

- **Ticket intake and classification** — analyze IT requests, assign categories and priorities, suggest resolutions, and identify tickets requiring escalation.
- **Helpdesk chatbot** — submit IT issues and retrieve relevant knowledge-base guidance.
- **ITSM dashboard** — browse tickets, filter by status and priority, and inspect ticket details.
- **RAG knowledge base** — search IT support articles and provide grounded troubleshooting guidance. The project falls back to lexical-overlap scoring when transformer embeddings are unavailable.
- **Self-healing workflow demonstrations** — examples include password reset, account unlock, VPN checks, and software installation requests.
- **Software provisioning catalogue** — validate supported software requests and display provisioning records.
- **ServiceNow integration layer** — support the configured ServiceNow integration or a mock/fallback mode, depending on environment settings.
- **Automation audit trail** — record simulated or executed workflow actions for inspection.
- **AI analysis inspector** — explore classification output, priority, confidence, and suggested actions.

## Technology stack

| Area | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript |
| Backend | Python, FastAPI, Pydantic |
| Data storage | MongoDB Atlas with local in-memory fallback |
| AI / NLP | Optional local Ollama LLM (default), optional Hugging Face Inference, sentence-transformers embeddings, rule-based classification and lexical fallback |
| Vector database | ChromaDB persistent collection with lexical fallback when embeddings / Chroma are unavailable |
| Integrations | ServiceNow REST integration or mock mode |
| API documentation | FastAPI / Swagger UI |

## Architecture

```text
Employee / Helpdesk UI (React + Vite)
                 |
             REST / JSON
                 |
         FastAPI application
                 |
    +------------+-------------+
    |            |             |
Ticket analysis  RAG / KB   ServiceNow/mock
    |            |
Automation       Knowledge articles
    |            |
Provisioning + audit
                 |
       overlapping text chunks
                 |
sentence-transformers embeddings
                 |
        ChromaDB vector search
                 |
  Retrieved chunks + source attribution
                 |
 Ollama local generation or grounded fallback
                 |
      MongoDB Atlas / local fallback
```

## Repository layout

```text
.
├── backend/
│   ├── app/
│   │   ├── database/
│   │   ├── models/
│   │   ├── routes/
│   │   └── services/
│   ├── knowledge_base.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
└── test_scenarios.py
```

## Run locally

### 1. Clone the repository

```powershell
git clone https://github.com/kethandeepakram/AI-ITSM-HELPDESK-NEW.git
cd AI-ITSM-HELPDESK-NEW
```

### 2. Install Ollama for local inference (Option B)

Install Ollama for your operating system from the official download page:
https://ollama.com/download

Then open a terminal and download a model. The configured default is:

```powershell
ollama pull qwen2.5:3b
```

Ollama should be running locally. Confirm the model is available with:

```powershell
ollama list
```

No Hugging Face inference token is required when `LLM_PROVIDER=ollama`. The RAG embeddings remain separate from text generation; sentence-transformers/Chroma may still download the configured embedding model on the first run.

### 3. Configure backend

From the repository root, create a local environment file:

```powershell
Copy-Item backend/.env.example backend/.env
```

Leave `HF_TOKEN=` empty and confirm these settings are present:

```dotenv
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=qwen2.5:3b
OLLAMA_TIMEOUT_SECONDS=45
```

Install dependencies and start FastAPI:

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Useful endpoints:
- API root: http://localhost:8000/
- Health check: http://localhost:8000/health
- Swagger UI: http://localhost:8000/docs

If Ollama is unavailable or the model is not installed, the app automatically uses its existing knowledge-base response fallback.

### 4. Start the frontend

Open another terminal at repository root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite (usually http://localhost:5173).

### 5. Run regression tests

From the repository root:

```powershell
python -m pytest -q test_scenarios.py
```

Review actual test output before treating tests as passed. The test suite contains an existing Hugging Face-specific mocked test; update its provider setting to `LLM_PROVIDER=huggingface` if you need to explicitly verify that optional hosted path.

## Example scenarios

1. **VPN support:** “I cannot connect to the company VPN.”
2. **Password assistance:** “I forgot my password and need to reset it.”
3. **Software request:** “Please install Visual Studio Code on my laptop.”
4. **Critical incident:** “The production server is down and multiple employees cannot access the application.”
5. **Knowledge search:** “How do I troubleshoot Outlook synchronization?”

Critical incidents and low-relevance knowledge matches should trigger the safety policy, not LLM-generated fixes. Automation displayed by the prototype may be simulated and should not be interpreted as confirmation that a real corporate system was changed.

## Security and operational notes

- Never commit a real `.env` file, credentials, or inference tokens.
- Keep CORS restricted to the frontend origins you use.
- Add authentication and authorization and protect administrative endpoints before any internet-facing deployment.
- Treat account/password reset and provisioning routines as demonstrations unless connected to and validated against authorized systems.
- The prototype is not a production-ready ITSM replacement.

## Known limitations

- RAG uses embeddings/ChromaDB when available and lexical-overlap retrieval when they are not. Lexical retrieval is not vector search.
- Ollama performs inference on the computer where its service runs; a hosted Render backend cannot reach your personal computer's `localhost`.
- ServiceNow and self-healing behaviors may use mock implementations depending on configuration.
- The local in-memory database fallback is not durable across process restarts.

## Future improvements

- Add authentication and authorization, deployment health checks, and automated regression coverage for connected and fallback modes.

---

Built as a portfolio prototype to explore AI-assisted IT support, ticket routing, knowledge retrieval, integration patterns, and auditability.
