from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama


# todo: switch to GroqCloud, use Llama 4 Maverick (17Bx128E)

OLLAMA_MODEL = "llama3-groq-tool-use:8b"
# GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


class CoreLLM:
    _llm = None

    def __new__(cls, *args, **kwargs) -> BaseChatModel:
        if cls._llm:
            return cls._llm
        cls._llm = ChatOllama(model=OLLAMA_MODEL)
        return cls._llm
