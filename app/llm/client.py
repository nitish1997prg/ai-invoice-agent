import os
from langchain_ollama import ChatOllama
from app.config.settings import get_settings
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OLLAMA_API_KEY")

def get_llm() -> ChatOllama:
    settings = get_settings()
    return ChatOllama(
    model=settings.ollama_chat_model,
    base_url=settings.ollama_base_url,
    client_kwargs={
        "headers": {
            "Authorization": f"Bearer {api_key}"
        }
    },
    temperature=0
)