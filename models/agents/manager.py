from typing import Literal

from models.agents.base import Agent
from prompts.manager import manager_system_prompt
from tools.manager import manager_toolset


class Manager(Agent):
    # tree node - dispatches sub-managers and workers
    type: Literal["manager"] = "manager"
    children: list[Agent] = []
    available_tools = manager_toolset

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
