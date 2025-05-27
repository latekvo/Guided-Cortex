from typing import Literal

from models.agents.base import Agent
from prompts.worker import worker_system_prompt
from tools.worker import worker_toolset


class Worker(Agent):
    # tree leaf - access to practical tools
    type: Literal["worker"] = "worker"
    # devices: list[VirtualDevice] # device system which extends available tooling, overkill for now
    available_tools = worker_toolset

    def _generate_prompt(self):
        return (
            f"{worker_system_prompt}\n\n"
            f"{self._chats_part()}\n\n"
            f"{self._log_part()}\n\n"
            f"{self._task_part()}"
        )
