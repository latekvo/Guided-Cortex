from langchain_core.messages import BaseMessage


class ExternalChat:
    def __init__(self, target_id: str, target_label: str):
        self.target_id: str = target_id
        self.target_label: str = target_label
        self.chat_history: list[BaseMessage] = []


def create_chat_pair(
    starter_id: str,
    target_id: str,
    starter_label: str,
    target_label: str,
) -> tuple[ExternalChat, ExternalChat]:
    # todo: trivial - move to pool
    chat_s = ExternalChat(target_id, target_label)
    chat_t = ExternalChat(starter_id, starter_label)
    return chat_s, chat_t
