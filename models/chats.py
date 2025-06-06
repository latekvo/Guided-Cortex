from langchain_core.messages import BaseMessage, AIMessage, HumanMessage


class ExternalChat:
    def __init__(self, target_id: str):
        self.target_id: str = target_id
        self.chat_history: list[BaseMessage] = []
        # Note: Circ ref - requires manual dealloc
        self.target_chat_ref: ExternalChat | None = None

    def send_message(self, message: str):
        """Send message to the chat recipients. To be used exclusively by the owner of the chat instance."""
        # todo: add sender ID? It's gonna be interpreted as just user-sent content by the newest models.
        #       should probably add SystemMessage notes "now speaking with" or "Chat between YOU and XYZ"
        self.chat_history.append(AIMessage(message))
        self.target_chat_ref.chat_history.append(HumanMessage(message))


def create_chat_pair(
    starter_id: str, target_id: str, opening_message: str
) -> tuple[ExternalChat, ExternalChat]:
    chat_a = ExternalChat(starter_id)
    chat_b = ExternalChat(target_id)
    chat_a.target_chat_ref = chat_b
    chat_b.target_chat_ref = chat_a
    chat_a.chat_history.append(AIMessage(opening_message))
    chat_b.chat_history.append(HumanMessage(opening_message))
    return chat_a, chat_b
