from typing import Literal

from langchain_core.messages import SystemMessage
from langchain_core.tools import tool

from models.agents.base import Agent
from prompts.overseer import overseer_system_prompt


class Overseer(Agent):
    @tool
    def approve_task(
        self,
    ):
        """Approves the creation of a child with the designated task."""
        pass

    @tool
    def modify_and_approve_task(
        self, new_task: str, executor: Literal["worker", "manager"]
    ):
        """Modifies the task details and approves it. Make sure to ask the requester before making any changes."""
        pass

    @tool
    def deny_task_creation(self, denial_reason: str):
        """Deny creation of the task. Make sure to discuss with the requester for their reasoning before denying a task."""
        pass

    # tree manager, trimmer and grower - independent of tree structure
    type: Literal["overseer"] = "overseer"

    def __init__(self, parent_id, task, label):
        super().__init__(parent_id, task, label)
        self._available_tools += [
            self.approve_task,
            self.modify_and_approve_task,
            self.deny_task_creation,
        ]

    def _generate_prompt(self):
        return [
            # todo: split up properly
            SystemMessage(
                f"{overseer_system_prompt}\n\n"
                f"{self._child_status_part()}\n\n"
                f"{self._chat_part()}\n\n"
                f"{self._task_part()}"
            )
        ]
