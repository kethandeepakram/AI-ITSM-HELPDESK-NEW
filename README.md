# SORIM.Ai Technical Hackathon Assessment
## AI-Powered ITSM & Intelligent Helpdesk Automation Platform

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%2018-61DAFB.svg)](https://reactjs.org/)
[![Hugging Face](https://img.shields.io/badge/LLM-Hugging%20Face%20Open--Source-FFA000.svg)](https://huggingface.co/)
[![ServiceNow](https://img.shields.io/badge/ITSM-ServiceNow%20REST%20API-81B5A1.svg)](https://www.servicenow.com/)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB%20Atlas-47A248.svg)](https://www.mongodb.com/atlas)

A complete enterprise-grade prototype designed for the **SORIM.Ai Technical Hackathon Assessment**. Demonstrates an end-to-end intelligent support journey:
**Employee Request $\rightarrow$ AI Understanding $\rightarrow$ Knowledge Retrieval (RAG) $\rightarrow$ Intelligent Decisioning $\rightarrow$ Self-Healing Automation $\rightarrow$ ServiceNow Integration $\rightarrow$ Audit Trail & Governance.**

---

## 1. System Architecture

```
[Employee Self-Service Portal / ITSM Admin UI] (React.js + Vite)
   │
   ├── 1. Employee Self-Service (AI Chatbot, Quick Resolvers, Ticket Submission)
   ├── 2. ITSM Dashboard (Metrics, Status, Audit Trail, Software Provisioning)
   ├── 3. AI Analysis Inspector (Confidence, Attribution, Classification, ServiceNow Field Mapping)
   └── 4. Knowledge Base (Category Browser, Dense + Sparse Semantic Vector Search)
             │
             ▼ REST API (JSON)
[Python FastAPI Backend Engine]
   │
   ├── [AI Intent & Safety Engine]
   │     • Intent Classification (Incident, Service Request, Knowledge, Automatable)
   │     • Priority Calculation (P1-P4) & Urgency/Impact Matrix
   │     • Assignment Group Routing (Network Support, IAM, Desktop Support, etc.)
   │     • Confidence Meter (0-100%) & Human Escalation Threshold Guard (< 65%)
   │     • Anti-Hallucination Policy Guard
   │
   ├── [RAG Knowledge Retrieval Pipeline]
   │     • 7+ Enterprise IT Support SOP Documents
   │     • Document Chunking & Hybrid Dense/Sparse Embeddings (all-MiniLM-L6-v2)
   │     • Vector Distance Re-Ranking & Grounded LLM Generation
   │
   ├── [Self-Healing & Provisioning Automation]
   │     • Automated Workflows: Password Reset, Account Unlock, VPN Check, Service Restart, Cache Purge
   │     • Software Catalog Validation (VS Code, Docker, Teams, Postman)
   │     • Mock Provisioning API & Complete Immutable Audit Trail
   │
   ├── [ServiceNow Integration Engine]
   │     • ServiceNow Table REST API (`/api/now/table/incident`)
   │     • ServiceNow Request API (`/api/now/table/sc_request`)
   │     • High-fidelity Mock ServiceNow Provider (Zero-config fallback)
   │
   └── [Data & Storage Layer]
         • MongoDB Atlas Cloud Collections: `tickets`, `knowledge_articles`, `automation_audit`, `software_provisioning`, `servicenow_incidents`
         • Built-in local persistence fallback for offline or zero-config execution
```

---

## 2. Technology Choices & Justification

| Layer | Technology | Engineering Rationale |
|---|---|---|
| **Frontend** | React 18, Vite | Component-driven architecture, ultra-fast HMR, clean state isolation between Chatbot, Dashboard, and AI Inspector. |
| **Backend** | Python 3.12 + FastAPI | Async high throughput, native OpenAPI/Swagger documentation, seamless integration with Hugging Face & vector libraries. |
| **LLM** | Hugging Face Open-Source (`Qwen2.5-3B-Instruct` / `Llama-3.2-3B`) | Open-weight enterprise models provide auditability, data privacy, and zero licensing cost compared to proprietary models. |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` | Fast 384-dimensional dense semantic vectors ideal for enterprise IT runbooks with minimal latency. |
| **Vector Search** | In-Memory Cosine Similarity + TF-IDF Re-Ranking | Hybrid retrieval (Dense Semantic + Sparse Keyword overlap) preventing out-of-domain hallucinations. |
| **Database** | MongoDB Atlas Cloud | Schema flexibility for varying incident schemas, audit log persistence, and native JSON documents. |
| **ITSM** | ServiceNow REST Table API | Industry gold standard ITSM platform. Dual-mode support (Live Developer Instance or Realistic Mock Provider). |

---

## 3. Five Mandatory Live Demonstration Scenarios

This platform includes a **1-Click Live Demo Launcher** in the UI and an automated Python test runner (`python test_scenarios.py`) covering all required scenarios:

### Scenario 1: Intelligent Ticket Intake
- **Prompt**: `"I cannot connect to VPN since this morning. Authentication keeps failing."`
- **AI Classification**:
  - **Intent**: `Incident`
  - **Category / Sub-category**: `Network / VPN`
  - **Priority**: `P2`
  - **Impact / Urgency**: `Individual / High`
  - **Assignment Group**: `Network Support`
  - **Summary**: `VPN authentication failure`
  - **Suggested Resolution**: `VPN troubleshooting`
- **Result**: Incident automatically generated and correlated with ServiceNow (`INC1000001`).

### Scenario 2: Auto Resolution / Self-Heal Agent
- **Prompt**: `"My password has expired."`
- **Execution Workflow**:
  `Identify` $\rightarrow$ `Diagnose` $\rightarrow$ `Knowledge Search` $\rightarrow$ `Determine Automation` $\rightarrow$ `Execute` $\rightarrow$ `Validate` $\rightarrow$ `Update ServiceNow` $\rightarrow$ `Audit Log`.
- **Result**: Password reset workflow completed, Active Directory flag cleared, ServiceNow Incident updated to `Resolved`, and action recorded in the security audit log.

### Scenario 3: Knowledge Management Automation (RAG)
- **Prompt**: `"How do I troubleshoot Outlook synchronization?"`
- **Pipeline**: Document $\rightarrow$ Chunking $\rightarrow$ Embedding $\rightarrow$ Semantic Search $\rightarrow$ LLM $\rightarrow$ Grounded Response.
- **Attribution**: Shows exact source article (`Microsoft Outlook Mailbox Synchronization Troubleshooting - KB1003`) with relevance score (98%).

### Scenario 4: Software Provisioning Automation
- **Prompt**: `"I need Visual Studio Code installed on my laptop."`
- **Expected Flow**: Employee $\rightarrow$ AI Intent Detection $\rightarrow$ Software Catalogue check $\rightarrow$ ServiceNow Request $\rightarrow$ Mock Provisioning API $\rightarrow$ Status Update.
- **UI Result**:
  - Request ID: `REQ001245`
  - Software: `Visual Studio Code`
  - Status: `Provisioning`
  - ServiceNow: `Request created successfully`

### Scenario 5: AI Safety, Governance & Escalation (Unknown Question)
- **Prompt**: `"Can you book a flight ticket to Paris for my vacation?"`
- **Anti-Hallucination Policy**: Detects non-IT out-of-scope query. Confidence drops to 32% (< 65% threshold).
- **Result**: Rejects ungrounded answer generation, informs user that approved KB lacks documentation, and automatically flags for human helpdesk escalation.

---

## 4. Required React Screens (Section 10)

1. **Employee Self-Service**:
   - AI Chatbot with interactive suggested resolutions and live status pills.
   - Quick self-healing resolver cards (Password, Account Unlock, VPN, Wi-Fi, Cache Purge).
   - 1-click incident submission.
2. **ITSM Dashboard**:
   - KPI metrics: Total Tickets, Open Tickets, AI-Resolved Tickets, Escalated Tickets, Software Requests, Audit Actions.
   - Filterable Tickets Table (by Status, Priority, Search Query).
   - Real-time ServiceNow synchronization indicators.
   - Dedicated Software Provisioning & Security Audit Trail tabs.
3. **AI Analysis Inspector**:
   - Interactive prompt analysis tool with confidence score gauge.
   - Grounding validation and anti-hallucination policy indicators.
   - Real-time ServiceNow REST Field Mapping matrix.
   - Ranked RAG attribution sources with similarity percentages.
4. **Knowledge Base**:
   - Category filtering (Network, Account & Access, Software, Hardware).
   - Semantic Vector Search test workbench.
   - Full article viewer with indexed keyword tags.

---

## 5. Setup & Running Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+

### Step 1: Clone & Configure Environment
```bash
git clone https://github.com/kethandeepakram/AI-ITSM-Helpdesk.git
cd AI-ITSM-Helpdesk

# Copy configuration template
cp .env.example backend/.env
```

If you have a **MongoDB Atlas URI** or **Hugging Face Token**, add them to `backend/.env`:
```env
MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority
HF_TOKEN=hf_your_token_here
```
*(Note: If left empty, the application automatically runs in zero-config offline mode with embedded local storage and fallback NLP/embeddings.)*

### Step 2: Start the Backend (FastAPI)
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
- API Documentation available at: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### Step 3: Start the Frontend (React + Vite)
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
- Open `http://localhost:5173` in your browser.

### Step 4: Run Automated Verification Tests
```bash
python test_scenarios.py
```
This executes all 5 Hackathon scenarios against the API and verifies expected outputs automatically!

---

## 6. 15–20 Minute Hackathon Presentation Script

| Time | Agenda Item | What to Say / Demonstrate |
|---|---|---|
| **0:00 - 2:00** | **Business Problem & Proposed Solution** | Traditional IT helpdesks suffer from high ticket volumes and repetitive L1 tasks (passwords, VPNs, software requests). Our platform automates repetitive resolution via AI Agents, RAG-grounded knowledge, and automated ServiceNow sync. |
| **2:00 - 5:00** | **Architecture & Technology Choices** | Explain the decoupled React + FastAPI architecture, why open-source Hugging Face models are chosen for enterprise privacy, and how MongoDB Atlas stores tickets and audit logs. |
| **5:00 - 13:00** | **Live Demonstration of the 5 Scenarios** | Use the top **Live Demo Launcher**: <br>1. Click Scenario 1: Show VPN intake and ServiceNow incident creation. <br>2. Click Scenario 2: Show password self-heal and ServiceNow update to Resolved. <br>3. Click Scenario 3: Show Outlook sync RAG search with KB1003 attribution. <br>4. Click Scenario 4: Show VS Code provisioning with REQ001245. <br>5. Click Scenario 5: Show flight booking rejection, confidence drop, and human escalation. |
| **13:00 - 15:00** | **AI / RAG & Vector DB Explanation** | Open the **AI Analysis Inspector** and **Knowledge Base** screens. Explain dense vector embeddings, cosine distance, and how the anti-hallucination guard protects enterprise governance. |
| **15:00 - 17:00** | **ServiceNow Integration & Automation** | Show the ITSM Dashboard table, the ServiceNow field mapping table, and the immutable audit log recording every automated action. |
| **17:00 - 20:00** | **Q&A & Future Roadmap** | Discuss multi-agent collaboration, containerized provisioning via Ansible/Terraform, and advanced fine-tuning on domain-specific IT logs. |

---

## 7. Submission Deliverables Checklist

- [x] Complete working frontend and backend running locally.
- [x] 5 Mandatory test scenarios covering all required use cases.
- [x] 4 Required React screens (Employee Self-Service, ITSM Dashboard, AI Analysis, Knowledge Base).
- [x] RAG pipeline with 7 sample enterprise IT support documents.
- [x] Self-healing suite (Password reset, Account unlock, VPN check, Service restart, Cache clear) with audit log.
- [x] Software Provisioning with Software Catalogue validation & Request ID tracking.
- [x] ServiceNow Table REST API client + realistic mock fallback.
- [x] AI Governance & Anti-Hallucination policy with confidence scoring (< 65% human escalation).
- [x] Automated test suite (`test_scenarios.py`).
- [x] Configuration instructions and `.env.example`.
#   A I - I T S M - H E L P D E S K - N E W  
 