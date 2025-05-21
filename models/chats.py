from langchain_core.messages import BaseMessage


class ExternalChat:
    initiator_id: str
    target_id: str
    opening_reason: str
    chat_summary: str
    chat_history: list[BaseMessage]
