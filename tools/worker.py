from langchain_core.tools import tool, BaseTool

from tools.universal import (
    broadcast_question,
    message_peer,
    close_peer_chat,
    message_superior,
)


@tool
def submit_work(work_result: str):
    """Submit your work once the work is high quality and working well."""
    pass


@tool
def run_linux_shell_command(command: str):
    """Runs a linux shell command."""
    pass


worker_toolset: list[BaseTool] = [
    broadcast_question,
    message_peer,
    close_peer_chat,
    message_superior,
    # unique tools
    submit_work,
    run_linux_shell_command,
]
