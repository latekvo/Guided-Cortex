from typing import Literal

from langchain_core.tools import tool

from models.agents.base import Agent
from prompts.manager import manager_system_prompt


class Manager(Agent):
    @tool
    def create_task(self, label: str, task: str):
        """Schedules creation and execution of the specified task."""
        pass

    @tool
    def accept_task_result(self, optional_comment: str):
        """Approve the work once it is high quality and working well."""
        pass

    @tool
    def terminate_task(self, task_id: str):
        """Stops task execution, whether it is finished or still executing."""
        pass

    # tree node - dispatches sub-managers and workers
    type: Literal["manager"] = "manager"
    children: list[Agent]

    def __init__(self, task):
        super().__init__(task)
        self.children = []
        self.available_tools += [
            self.create_task,
            self.accept_task_result,
            self.terminate_task,
        ]

    def run_turn_recurse(self):
        # this is only an approximation of inverse bfs
        # the primary point is to execute all workers before the managers
        for child in self.children:
            if isinstance(child, Manager):
                child.run_turn_recurse()
            else:
                # Worker, verifier or overseer
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
