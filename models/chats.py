from langchain_core.messages import BaseMessage


class ExternalChat:
    # Note: ExternalChat requires manual dealloc
    def __init__(self, init_id: str, target_id: str, opening_reason: str):
        self.initiator_id: str = init_id
        self.target_id: str = target_id
        self.opening_reason: str = opening_reason
        self.chat_history: list[BaseMessage] = []
        self.target_chat_ref: ExternalChat | None = None
