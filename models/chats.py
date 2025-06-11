from langchain_core.messages import BaseMessage, AIMessage, HumanMessage


class ExternalChat:
    def __init__(
        self,
        target_id: str,
        target_label: str,
        target_log_chat: list[BaseMessage],
    ):
        self.target_id: str = target_id
        self.target_label: str = target_label
        self.chat_history: list[BaseMessage] = []
        # Note: Circ ref - requires manual dealloc
        self.target_chat_ref: ExternalChat | None = None
        self.target_log_chat: list[BaseMessage] = target_log_chat  # ref

    def send_message(self, message: str):
        """Send message to the chat recipients. To be used exclusively by the owner of the chat instance."""
        # todo: add sender ID? It's gonna be interpreted as just user-sent content by the newest models.
        #       should probably add SystemMessage notes "now speaking with" or "Chat between YOU and XYZ"
        self.chat_history.append(AIMessage(message))
        self.target_chat_ref.chat_history.append(HumanMessage(message))
        clean_msg = message.replace("\n", "<br>")
        msg_notify = HumanMessage(
            f"Notification: new message from {self.target_label} ({self.target_id}): {clean_msg}"
        )
        self.target_log_chat.append(msg_notify)


def create_chat_pair(
    starter_id: str,
    target_id: str,
    starter_label: str,
    target_label: str,
    opening_message: str,
    self_log_chat: list[BaseMessage],
    target_log_chat: list[BaseMessage],
) -> tuple[ExternalChat, ExternalChat]:
    chat_s = ExternalChat(target_id, target_label, target_log_chat)
    chat_t = ExternalChat(starter_id, starter_label, self_log_chat)
    chat_s.target_chat_ref = chat_t
    chat_t.target_chat_ref = chat_s
    chat_s.chat_history.append(AIMessage(opening_message))
    chat_t.chat_history.append(HumanMessage(opening_message))
    return chat_s, chat_t
