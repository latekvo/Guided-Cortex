from typing import Callable

from langchain_core.messages import BaseMessage, AIMessage, HumanMessage


class ExternalChat:
    def __init__(self, target_id: str, target_label: str, notify_cb: Callable):
        notify_cb()
        self.target_id: str = target_id
        self.target_label: str = target_label
        self.chat_history: list[BaseMessage] = []
        self.target_chat_ref: ExternalChat | None = None

    def send_message(self, message: str):
        """Send message to the chat recipients. To be used exclusively by the owner of the chat instance."""
        self.chat_history.append(AIMessage(message))
        self.target_chat_ref.chat_history.append(HumanMessage(message))


def create_chat_pair(
    starter_id: str,
    target_id: str,
    starter_label: str,
    target_label: str,
    notify_starter_cb: Callable,
    notify_target_cb: Callable,
    opening_message: str,
) -> tuple[ExternalChat, ExternalChat]:
    # fixme: can't just use Agent class due to circ dep
    #        ^ resolve via global id pool
    chat_s = ExternalChat(target_id, target_label, notify_starter_cb)
    chat_t = ExternalChat(starter_id, starter_label, notify_target_cb)
    chat_s.target_chat_ref = chat_t
    chat_t.target_chat_ref = chat_s
    chat_s.chat_history.append(AIMessage(opening_message))
    chat_t.chat_history.append(HumanMessage(opening_message))
    return chat_s, chat_t
