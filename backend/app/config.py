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

    # Comma-separated allowed browser origins. Set these to frontend origin(s).
    CORS_ORIGINS: list[str] = [
        origin.strip().rstrip("/")
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ]

    # MongoDB Atlas
    MONGODB_URI: str | None = os.getenv("MONGODB_URI")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "itsm_helpdesk")

    # Optional hosted Hugging Face inference. Keep blank to avoid paid inference.
    HF_TOKEN: str | None = os.getenv("HF_TOKEN")
    HF_LLM_MODEL: str = os.getenv("HF_LLM_MODEL", "Qwen/Qwen2.5-3B-Instruct")
    HF_EMBEDDING_MODEL: str = os.getenv(
        "HF_EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    )

    # Option B: Ollama local inference (no hosted inference credits).
    # Ollama must be installed and the configured model pulled locally.
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    OLLAMA_LLM_MODEL: str = os.getenv("OLLAMA_LLM_MODEL", "qwen2.5:3b")
    OLLAMA_TIMEOUT_SECONDS: float = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "45"))

    # Chroma persistent vector database (local prototype storage).
    CHROMA_PERSIST_DIRECTORY: str = os.getenv(
        "CHROMA_PERSIST_DIRECTORY",
        str(backend_dir / "chroma_data"),
    )
    CHROMA_COLLECTION_NAME: str = os.getenv(
        "CHROMA_COLLECTION_NAME",
        "itsm_knowledge_chunks",
    )

    # ServiceNow Configuration
    SERVICENOW_INSTANCE_URL: str | None = os.getenv("SERVICENOW_INSTANCE_URL")
    SERVICENOW_USERNAME: str | None = os.getenv("SERVICENOW_USERNAME")
    SERVICENOW_PASSWORD: str | None = os.getenv("SERVICENOW_PASSWORD")
    SERVICENOW_MOCK_MODE: bool = os.getenv("SERVICENOW_MOCK_MODE", "true").lower() in ("true", "1", "yes")

    # AI Safety & Governance
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.65"))

settings = Settings()
