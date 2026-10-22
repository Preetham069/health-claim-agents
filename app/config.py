import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings(BaseModel):
    google_api_key: str = Field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", ""))
    ollama_base_url: str = Field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    ollama_chat_model: str = Field(default_factory=lambda: os.getenv("OLLAMA_CHAT_MODEL", "qwen2:7b"))
    ollama_embed_model: str = Field(default_factory=lambda: os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"))
    gemini_model_fast: str = Field(default_factory=lambda: os.getenv("GEMINI_MODEL_FAST", "gemini-1.5-flash"))
    gemini_model_pro: str = Field(default_factory=lambda: os.getenv("GEMINI_MODEL_PRO", "gemini-1.5-pro"))
    risk_review_threshold: int = Field(default_factory=lambda: int(os.getenv("RISK_REVIEW_THRESHOLD", "50")))
    base_dir: Path = BASE_DIR
    data_dir: Path = BASE_DIR / "data"
    chroma_dir: Path = BASE_DIR / "chroma_db"
    db_path: Path = BASE_DIR / "claims.db"

settings = Settings()