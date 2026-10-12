# SORIM.Ai — AI-Powered ITSM Helpdesk

An AI-assisted IT service desk prototype built with **React, FastAPI, MongoDB, retrieval-augmented generation (RAG), and simulated self-healing workflows**. It demonstrates how an employee issue can be classified, linked to knowledge-base guidance, recorded as a ticket, and routed toward automation or human escalation.

> **Prototype note:** Integrations and remediation workflows may be simulated or use fallback behavior when external services are not configured. Do not use this project to perform real production changes without adding appropriate authentication, authorization, safeguards, and operational validation.

## Features

- **Ticket intake and classification** — analyze IT requests, assign categories and priorities, suggest resolutions, and identify tickets requiring escalation.
- **Helpdesk chatbot** — submit IT issues and retrieve relevant knowledge-base guidance.
- **ITSM dashboard** — browse tickets, filter by status and priority, and inspect ticket details.
- **RAG knowledge base** — search IT support articles and provide grounded troubleshooting guidance. The project can fall back to TF-IDF when transformer embeddings are unavailable.
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
| AI / NLP | Hugging Face Inference API (optional), sentence-transformers (optional), rule-based classification, TF-IDF fallback |
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
Ticket analysis  RAG / KB   ITSM integration
    |            |             |
Automation eligibility      ServiceNow/mock
    |
Provisioning + audit records
                 |
        MongoDB / local fallback
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
│   ├── seed_knowledge.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
├── test_scenarios.py
├── .env.example
├── .gitignore
└── README.md
```

The exact files may evolve as the project is developed.

## Prerequisites

- Python 3.10 or later
- Node.js 18 or later and npm
- Git

MongoDB Atlas and a Hugging Face token are optional for basic local exploration if the fallback modes remain enabled in your configuration.

## Run locally

### 1. Clone the repository

```bash
git clone https://github.com/kethandeepakram/AI-ITSM-HELPDESK-NEW.git
cd AI-ITSM-HELPDESK-NEW
```

### 2. Configure the backend

Create a local environment file by copying the template. On Windows PowerShell:

```powershell
Copy-Item backend/.env.example backend/.env
```

If your project uses the root-level template instead, copy that template and adapt the destination to the variables expected by `backend/app/config.py`.

Open `backend/.env` and set the values needed by your configuration. For example:

```dotenv
MONGODB_URI=
MONGODB_DATABASE=itsm_helpdesk
HF_TOKEN=
```

Use the variable names required by your local configuration. Leave optional integrations blank when you want to use fallback mode. **Never commit your real `.env` file, credentials, or API tokens.**

Install backend dependencies and start FastAPI:

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Useful local endpoints:

- API root: http://localhost:8000/
- Health check: http://localhost:8000/health
- Interactive API docs: http://localhost:8000/docs

Keep this terminal running.

### 3. Start the frontend

Open a second terminal at the repository root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite (usually http://localhost:5173).

Make sure the frontend API base URL in `frontend/src/services/api.js` matches the backend URL used locally or in your deployment.

### 4. Run scenario tests

From the repository root, review the test script's prerequisites and then run:

```powershell
python test_scenarios.py
```

The test script may require the backend to be running. Review its output and the application's actual responses; this README does not claim tests have been run in every environment.

## Example scenarios to try

1. **VPN support:** “I cannot connect to the company VPN.”
2. **Password assistance:** “I forgot my password and need to reset it.”
3. **Software request:** “Please install Visual Studio Code on my laptop.”
4. **Critical incident:** “The production server is down and multiple employees cannot access the application.”
5. **Knowledge search:** “How do I troubleshoot Outlook synchronization?”

Expected behavior depends on the configured rules and external integrations. Critical production incidents should be escalated rather than automatically remediated by an unrelated action. Automation displayed by the prototype may be simulated and should not be interpreted as confirmation that a real corporate system was changed.

## Security and operational notes

- Do not upload `.env` files or secrets to GitHub.
- Use `.env.example` only for placeholder values.
- Restrict CORS, add authentication and authorization, validate inputs, and protect administrative endpoints before any internet-facing deployment.
- Treat account/password reset, service restart, and provisioning routines as demonstrations unless connected to and validated against authorized systems.
- Use persistent storage and audit retention policies appropriate to your environment if adapting the prototype for real use.

## Known limitations

- If sentence-transformers cannot load, knowledge retrieval may use the TF-IDF fallback rather than dense embeddings.
- ServiceNow and self-healing behaviors may use mock implementations depending on configuration.
- The local in-memory database fallback is not durable across process restarts.
- The prototype is not a production-ready ITSM replacement.

## Future improvements

- Add automated backend and frontend tests to CI.
- Add role-based authentication and authorization.
- Improve retrieval evaluation, source attribution, and embedding setup.
- Add structured configuration validation and health checks for connected services.
- Add deployment guides and verified screenshots of the application.

## License

No license is currently specified. Add a license file if you want to explicitly define how others may use, modify, and redistribute this project.

---

Built as a portfolio prototype to explore AI-assisted IT support, ticket routing, knowledge retrieval, integration patterns, and auditability.
