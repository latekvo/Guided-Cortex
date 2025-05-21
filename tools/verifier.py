from langchain_core.tools import tool, BaseTool

from tools.universal import close_peer_chat, message_peer, broadcast_question


# Tasks have to be approved by verifiers before being sent over to manager
# We cannot afford managers wasting their context & time on technical reviews


@tool
def approve_work(optional_comment: str):
    """Approve the work once it is high quality and working well."""
    pass


@tool
def request_changes(requested_changes: str):
    """Reports all issues found within the proposed work, requests their improvement."""
    pass


verifier_toolset: list[BaseTool] = [
    broadcast_question,
    message_peer,
    close_peer_chat,
    # no manager, contact_manager omitted
    # unique tools
    approve_work,
    request_changes,
]
