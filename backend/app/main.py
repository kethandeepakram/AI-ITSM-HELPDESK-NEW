from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chatbot import router as chatbot_router
from app.routes.tickets import router as tickets_router
from app.routes.provisioning import router as provisioning_router
from app.routes.knowledge import router as knowledge_router
from app.routes.servicenow import router as servicenow_router
from app.routes.audit import router as audit_router
from app.routes.demo import router as demo_router
from seed_knowledge import seed_knowledge_base
from app.config import settings

app = FastAPI(
    title="AI-Powered ITSM & Intelligent Helpdesk Automation Platform",
    description="Enterprise-grade AI Helpdesk automation prototype with ServiceNow integration",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    # The frontend does not use cookie-based authentication.
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(chatbot_router)
app.include_router(tickets_router)
app.include_router(provisioning_router)
app.include_router(knowledge_router)
app.include_router(servicenow_router)
app.include_router(audit_router)
app.include_router(demo_router)

@app.on_event("startup")
def startup_event():
    try:
        seed_knowledge_base()
        print("[Startup] Knowledge Base initialized successfully.")
    except Exception as e:
        print(f"[Startup] Note on seeding knowledge base: {e}")

@app.get("/")
def root():
    return {
        "message": "AI-Powered ITSM Helpdesk Automation Platform API",
        "status": "running",
        "docs_url": "/docs"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "itsm-helpdesk-api"
    }