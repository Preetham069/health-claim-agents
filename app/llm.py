import logging
from typing import Any
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings

logger = logging.getLogger("LLMFactory")

class LLMFactory:
    @staticmethod
    def get_ollama_chat(model: str | None = None, temperature: float = 0.0) -> ChatOllama:
        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=model or settings.ollama_chat_model,
            temperature=temperature,
        )

    @staticmethod
    def get_ollama_embeddings() -> OllamaEmbeddings:
        return OllamaEmbeddings(
            base_url=settings.ollama_base_url,
            model=settings.ollama_embed_model,
        )

    @staticmethod
    def get_gemini_chat(model: str | None = None, temperature: float = 0.0) -> Any:
        target = model or settings.gemini_model_fast
        if not settings.google_api_key or settings.google_api_key == "your_gemini_api_key_here":
            logger.warning("No valid API key. Falling back to Ollama.")
            return LLMFactory.get_ollama_chat(temperature=temperature)
        try:
            return ChatGoogleGenerativeAI(
                model=target,
                google_api_key=settings.google_api_key,
                temperature=temperature,
            )
        except Exception as e:
            logger.error(f"Gemini init failed ({e}). Falling back to Ollama.")
            return LLMFactory.get_ollama_chat(temperature=temperature)