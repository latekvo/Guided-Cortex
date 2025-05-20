from typing import Literal

from langchain_core.language_models import BaseLLM
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool, BaseTool


@tool
def create_task(label: str, task: str):
    """Schedules creation and execution of the specified task."""
    pass


@tool
def terminate_task(task_id: str):
    """Stops task execution, whether it is finished or still executing."""
    pass


@tool
def submit_work(work_result: str):
    """Submit your work once the work is high quality and working well."""
    pass


@tool
def approve_work(optional_comment: str):
    """Approve the work once it is high quality and working well."""
    pass


@tool
def request_changes(requested_changes: str):
    """Reports all issues found within the proposed work, requests their improvement."""
    pass


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
def contact_manager(message: str):
    """Sends message to your manager."""
    # direct communication with parent
    pass


@tool
def run_linux_shell_command(command: str):
    """Runs a linux shell command."""
    pass


# note: We're not doing any persistent thinking functions
#       Managers should be able to divide the tasks and respond to events,
#       anything more will clog up context. Answer-time reasoning should be enough.
#       Workers even more so, their tasks are all 1-turn + corrections hopefully,
#       a longer chain of though should be replaced by a deeper hierarchy where possible.

complete_toolset: list[BaseTool] = [
    approve_work,
    submit_work,
    terminate_task,
    create_task,
    request_changes,
    broadcast_question,
    message_peer,
    close_peer_chat,
    contact_manager,
    run_linux_shell_command,
]

verifier_toolset: list[BaseTool] = [
    broadcast_question,
    message_peer,
    close_peer_chat,
    # no manager, contact_manager omitted
    # unique tools
    approve_work,
    request_changes,
]

manager_toolset: list[BaseTool] = [
    broadcast_question,
    message_peer,
    close_peer_chat,
    contact_manager,
    # unique tools
    create_task,
    terminate_task,
]

worker_toolset: list[BaseTool] = [
    broadcast_question,
    message_peer,
    close_peer_chat,
    contact_manager,
    # unique tools
    submit_work,
    run_linux_shell_command,
]

# note: there doesn't seem to be a need for an id-based pool of agents, thus sticking to a ref-tree


class ExternalChat:
    initiator_id: str
    target_id: str
    opening_reason: str
    chat_summary: str
    chat_history: list[BaseMessage]


class Agent:
    id: str  # unique but readable, max 8 base36 chars
    label: str  # non-unique
    type: Literal["overseer", "manager", "worker", "verifier"]

    available_tools: list[BaseTool]
    interface_chat: list[BaseMessage]  # tool calls, UI & notes
    external_chats: list[ExternalChat]  # chats opened with other agents

    # metadata
    task: str
    system_prompt: str
    llm: BaseLLM  # ref to predefined class


class Overseer(Agent):
    # tree manager, trimmer and grower - independent of tree structure
    type: Literal["overseer"] = "overseer"


class Manager(Agent):
    # tree node - dispatches sub-managers and workers
    type: Literal["manager"] = "manager"
    children: list = []


class Environment:
    # internal
    # defines a broad feature requiring
    device: Literal["browser", "linux"]


class VirtualDevice:
    # defines connection to an atomic part of a broader system, e.g.: linux_shell
    kind: Literal["text_file", "file_tree", "browser", "webpage", "linux_shell"]
    environment: Environment  # ref to shared env


class Worker(Agent):
    # tree leaf - access to practical tools
    type: Literal["worker"] = "worker"
    # devices: list[VirtualDevice] # device system which extends available tooling, overkill for now


root_manager = Manager()


def main():
    return


main()
