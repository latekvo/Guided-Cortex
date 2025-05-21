from typing import Literal

from langchain_core.tools import tool, BaseTool

from tools.universal import broadcast_question, message_peer, close_peer_chat


# todo: Peer chat management will have to be done by a separate worker.


@tool
def approve_task():
    """Approves the creation of a child with the designated task."""
    pass


@tool
def modify_and_approve_task(new_task: str, executor: Literal["worker", "manager"]):
    """Modifies the task details and approves it. Make sure to ask the requester before making any changes."""
    pass


@tool
def deny_task_creation(denial_reason: str):
    """Deny creation of the task. Make sure to discuss with the requester for their reasoning before denying a task."""
    pass


overseer_toolset: list[BaseTool] = [
    broadcast_question,
    message_peer,
    close_peer_chat,
    # unique tools
    approve_task,
    modify_and_approve_task,
    deny_task_creation,
]
