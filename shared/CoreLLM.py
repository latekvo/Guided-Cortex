import os

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_groq import ChatGroq

load_dotenv()

OLLAMA_MODEL = "llama3-groq-tool-use:8b"
# GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"    # cheaper
GROQ_MODEL = "meta-llama/llama-4-maverick-17b-128e-instruct"  # better
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


class CoreLLM:
    _llm = None

    def __new__(cls, *args, **kwargs) -> BaseChatModel:
        if cls._llm:
            return cls._llm
        # cls._llm = ChatOllama(model=OLLAMA_MODEL)
        cls._llm = ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY)
        return cls._llm
