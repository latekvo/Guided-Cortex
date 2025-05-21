from langchain_core.tools import tool, BaseTool

from tools.universal import (
    broadcast_question,
    message_peer,
    close_peer_chat,
    message_superior,
)


@tool
def create_task(label: str, task: str):
    """Schedules creation and execution of the specified task."""
    pass


@tool
def accept_task_result(optional_comment: str):
    """Approve the work once it is high quality and working well."""
    pass


@tool
def terminate_task(task_id: str):
    """Stops task execution, whether it is finished or still executing."""
    pass


manager_toolset: list[BaseTool] = [
    broadcast_question,
    message_peer,
    close_peer_chat,
    message_superior,
    # unique tools
    create_task,
    terminate_task,
    accept_task_result,
]
