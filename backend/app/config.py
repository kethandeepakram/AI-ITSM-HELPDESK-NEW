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
    APP_NAME: str = "AI-Powered ITSM & Intelligent Helpdesk Automation Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    CORS_ORIGINS: list[str] = [
        origin.strip().rstrip("/")
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ]

    # MongoDB Atlas. If unavailable, the app falls back to temporary local storage.
    MONGODB_URI: str | None = os.getenv("MONGODB_URI")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "itsm_helpdesk")

    # Free/public Hugging Face model run locally using Transformers.
    # Public models do not require an HF token; do not paste secrets into source control.
    HF_TOKEN: str | None = os.getenv("HF_TOKEN") or None
    HF_LLM_MODEL: str = os.getenv(
        "HF_LLM_MODEL",
        "Qwen/Qwen2.5-1.5B-Instruct",
    )
    HF_EMBEDDING_MODEL: str = os.getenv(
        "HF_EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    )
    # transformers = local model; huggingface_api = hosted/credit-limited inference;
    # fallback = grounded knowledge retrieval without generation (useful for CI).
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "transformers").strip().lower()
    HF_MAX_NEW_TOKENS: int = int(os.getenv("HF_MAX_NEW_TOKENS", "220"))

    CHROMA_PERSIST_DIRECTORY: str = os.getenv(
        "CHROMA_PERSIST_DIRECTORY",
        str(backend_dir / "chroma_data"),
    )
    CHROMA_COLLECTION_NAME: str = os.getenv(
        "CHROMA_COLLECTION_NAME",
        "itsm_knowledge_chunks",
    )

    SERVICENOW_INSTANCE_URL: str | None = os.getenv("SERVICENOW_INSTANCE_URL")
    SERVICENOW_USERNAME: str | None = os.getenv("SERVICENOW_USERNAME")
    SERVICENOW_PASSWORD: str | None = os.getenv("SERVICENOW_PASSWORD")
    SERVICENOW_MOCK_MODE: bool = os.getenv(
        "SERVICENOW_MOCK_MODE", "true"
    ).lower() in ("true", "1", "yes")

    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.65"))


settings = Settings()
