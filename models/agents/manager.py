from typing import Literal

from langchain_core.messages import SystemMessage, BaseMessage
from langchain_core.tools import StructuredTool

from debug.tracer import Trace, trace
from models.agents.base import Agent
from models.agents.worker import Worker
from models.chats import create_chat_pair
from prompts.manager import manager_system_prompt


# Manager does not have a discrete submission function, we prefer for it to communicate actively.
# This is due to the Manager having a very broad, potentially dynamic task, with lots of room for discussion.
# To resolve context window issues, add a separate chat for pinned memories, actively shorten the regular chats.

# fixme: A high-level manager accidentally "accepting" the work of another high-leveler could be devastating.


class Manager(Agent):
    def _tool_create_task(
        self,
        label: str,
        task: str,
        # `task_type` is a temporary replacement for Overseer
        task_type: Literal["abstract", "technical"],
    ):
        if task_type == "abstract":
            child = Manager(self.id, task, label)
        else:
            child = Worker(self.id, task, label)

        trace(
            Trace.NEW_TASK, f'{self.label} creates {task_type} child "{child.label}".'
        )

        self.children.append(child)

        chat_for_self, chat_for_child = create_chat_pair(self.id, child.id, task)

        self.external_chats |= {child.id: chat_for_self}
        child.external_chats |= {self.id: chat_for_child}
        return f"Task '{child.id}' created successfully."

    def _tool_accept_task_result(self, task_id: str):
        # Task completion notification is delivered via UI.
        # This function simply closes the task if it's in a satisfactory state.
        child = self._get_child_by_id(task_id)
        chat = self._get_chat_by_target_id(task_id)
        if child is None or chat is None:
            return f"Error: Task {task_id} not found."

        trace(
            Trace.DEL_TASK,
            f"{self.label} removes {child.label}: ",
            "Task has been completed.",
        )

        del child.external_chats[self.id].target_chat_ref  # circ dep
        del child.external_chats[self.id]
        del self.external_chats[child.id].target_chat_ref  # circ dep
        del self.external_chats[child.id]
        self.children.remove(child)
        return f"Task {task_id} closed as completed."

    def _tool_deny_task_result(self, task_id: str, denial_reason: str):
        # While generally active communication is preferred,
        # there could be a situation where invalid work is submitted and successfully verified.
        trace(Trace.CHAT, f"{self.label} denies {task_id}'s work result.")

        chat = self._get_chat_by_target_id(task_id)
        if chat is None:
            return f"Error: Task {task_id} not found."
        chat.send_message(f"NOTIFICATION: Task result has been denied: {denial_reason}")
        return "Task result denied. Notified worker about the denial reason."

    def _tool_terminate_task(self, task_id: str):
        child = self._get_child_by_id(task_id)
        chat = self._get_chat_by_target_id(task_id)
        if child is None or chat is None:
            return f"Error: Task {task_id} not found."
        trace(Trace.DEL_TASK, f"{self.label} removes {child.label}")

        self.children.remove(child)
        del self.external_chats[child.id]
        return f"Task {task_id} successfully terminated."

    def _tool_skip_turn(self):
        trace(Trace.THINK, f"{self.label} skips turn.")
        return f"Turn skipped, passing time."

    # tree node - dispatches sub-managers and workers
    type: Literal["manager"] = "manager"
    children: list[Agent]

    def __init__(self, parent_id, task, label):
        super().__init__(parent_id, task, label)
        self.children = []
        self.available_tools += [
            StructuredTool.from_function(
                name="create_task",
                func=self._tool_create_task,
                description="Schedules creation and execution of the specified task.",
            ),
            StructuredTool.from_function(
                name="accept_task_result",
                func=self._tool_accept_task_result,
                description="Approve the work once it is high quality and working well.",
            ),
            StructuredTool.from_function(
                name="terminate_task",
                func=self._tool_terminate_task,
                description="Stops task execution, whether it is finished or still executing.",
            ),
        ]

    def _get_child_by_id(self, task_id) -> Agent | None:
        # todo: convert self.children to dict
        for child in self.children:
            if child.id == task_id:
                return child
        return None

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

    def _generate_prompt(self) -> list[BaseMessage]:
        return [
            SystemMessage(manager_system_prompt),
            self._task_part(),
            *self._chats_part(),
            *self._log_part(),
        ]
