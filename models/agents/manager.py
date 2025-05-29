from typing import Literal

from langchain_core.messages import AIMessage
from langchain_core.tools import tool

from models.agents.base import Agent
from models.agents.worker import Worker
from models.chats import ExternalChat
from prompts.manager import manager_system_prompt


# Manager does not have a discrete submission function, we prefer for it to communicate actively.
# This is due to the Manager having a very broad, potentially dynamic task, with lots of room for discussion.
# To resolve context window issues, add a separate chat for pinned memories, actively shorten the regular chats.


class Manager(Agent):
    @tool
    def create_task(
        self,
        label: str,
        task: str,
        # `task_type` is a temporary replacement for Overseer
        task_type: Literal["abstract", "technical"],
    ):
        """Schedules creation and execution of the specified task."""
        if task_type == "abstract":
            child = Manager(task, label)
        else:
            child = Worker(task, label)

        self.children.append(child)

        shared_chat = ExternalChat(self.id, child.id, "Creation of new task")
        self.external_chats.append(shared_chat)
        child.external_chats.append(shared_chat)

    @tool
    def accept_task_result(self, task_id: str):
        """Approve the work once it is high quality and working well."""
        # Task completion notification is delivered via UI.
        # This function simply closes the task if it's in a satisfactory state.
        # todo: add a confirmation or lock this function to low-nesting chats only
        #       a high-level manager accidentally "accepting" the work of another high-leveler
        #       could be devastating. Perhaps put spent agents to sleep until memory limit is hit?
        child = self._get_child_by_id(task_id)
        chat = self._get_chat_by_member_id(task_id)
        if child is None or chat is None:
            return f"Error: Task {task_id} not found."

        self.children.remove(child)
        self.external_chats.remove(chat)
        return f"Task {task_id} closed as completed."

    @tool
    def deny_task_result(self, task_id: str, denial_reason: str):
        """Deny the work submitted by one of your workers."""
        # While generally active communication is preferred,
        # there could be a situation where invalid work is submitted and successfully verified.
        chat = self._get_chat_by_member_id(task_id)

        if chat is None:
            return f"Error: Task {task_id} not found."

        # todo: add proper message author system
        chat.chat_history.append(
            AIMessage(f"NOTIFICATION: Task result has been denied: {denial_reason}")
        )
        return "Task result denied. Notified worker about the denial reason."

    @tool
    def terminate_task(self, task_id: str):
        """Stops task execution, whether it is finished or still executing."""
        child = self._get_child_by_id(task_id)
        chat = self._get_chat_by_member_id(task_id)
        if child is None or chat is None:
            return f"Error: Task {task_id} not found."

        self.children.remove(child)
        self.external_chats.remove(chat)
        return f"Task {task_id} successfully terminated."

    # tree node - dispatches sub-managers and workers
    type: Literal["manager"] = "manager"
    children: list[Agent]

    def __init__(self, task, label):
        super().__init__(task, label)
        self.children = []
        self.available_tools += [
            self.create_task,
            self.accept_task_result,
            self.terminate_task,
        ]

    def _get_child_by_id(self, task_id) -> Agent | None:
        for child in self.children:
            if child.id == task_id:
                return child

    def run_turn_recurse(self):
        # this is only an approximation of inverse bfs
        # the primary point is to execute all workers before the managers
        for child in self.children:
            if isinstance(child, Manager):
                child.run_turn_recurse()
            else:
                # Worker, Verifier or Overseer
                # verifiers and overseers may be children or peers of event initiators
                child.run_turn()
        self.run_turn()

    def _generate_prompt(self):
        return (
            f"{manager_system_prompt}\n\n"
            f"{self._chats_part()}\n\n"
            f"{self._log_part()}\n\n"
            f"{self._task_part()}"
        )
