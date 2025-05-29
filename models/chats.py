from langchain_core.messages import BaseMessage


class ExternalChat:
    initiator_id: str
    target_id: str
    opening_reason: str
    chat_summary: str
    chat_history: list[BaseMessage]

    def __init__(self, init_id: str, target_id: str, opening_reason: str):
        self.initiator_id = init_id
        self.target_id = target_id
        self.opening_reason = opening_reason
        # generate after every N turns, make it broad
        self.chat_summary = "Summary not available yet."
        self.chat_history = []
