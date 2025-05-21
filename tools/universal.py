from langchain_core.tools import tool


@tool
def broadcast_question(question: str):
    """Broadcasts a question within your team, opens a chat with the peer who can answer you."""
    # overseer determines if the question can and should be answered, then routes it appropriately
    pass


@tool
def message_peer(message: str, peer_id: str):
    """Sends a message in one of your open peer chats."""
    # opens communication with an agent relevant to request
    # we have to limit possible connections, they may eat up context
    pass


@tool
def close_peer_chat(peer_id: str):
    """Closes a chat once the original question has been resolved."""
    pass


@tool
def message_superior(message: str):
    """Sends message to your superior."""
    # direct communication with parent
    pass
