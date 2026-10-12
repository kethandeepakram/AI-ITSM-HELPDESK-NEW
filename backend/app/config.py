import os
from pathlib import Path
from dotenv import load_dotenv

# Search for .env in current backend dir or parent dir
backend_dir = Path(__file__).resolve().parent.parent
root_dir = backend_dir.parent

if (backend_dir / ".env").exists():
    load_dotenv(backend_dir / ".env")
elif (root_dir / ".env").exists():
    load_dotenv(root_dir / ".env")
else:
    load_dotenv()

class Settings:
    # Project Info
    APP_NAME: str = "AI-Powered ITSM & Intelligent Helpdesk Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # MongoDB Atlas
    MONGODB_URI: str | None = os.getenv("MONGODB_URI")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "itsm_helpdesk")

    # Hugging Face
    HF_TOKEN: str | None = os.getenv("HF_TOKEN")
    HF_LLM_MODEL: str = os.getenv("HF_LLM_MODEL", "Qwen/Qwen2.5-3B-Instruct")
    HF_EMBEDDING_MODEL: str = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    # ServiceNow Configuration
    SERVICENOW_INSTANCE_URL: str | None = os.getenv("SERVICENOW_INSTANCE_URL")
    SERVICENOW_USERNAME: str | None = os.getenv("SERVICENOW_USERNAME")
    SERVICENOW_PASSWORD: str | None = os.getenv("SERVICENOW_PASSWORD")
    SERVICENOW_MOCK_MODE: bool = os.getenv("SERVICENOW_MOCK_MODE", "true").lower() in ("true", "1", "yes")

    # AI Safety & Governance
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.65"))

settings = Settings()
