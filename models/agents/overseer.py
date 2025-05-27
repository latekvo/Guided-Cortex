from typing import Literal

from models.agents.base import Agent
from prompts.overseer import overseer_system_prompt
from tools.overseer import overseer_toolset


class Overseer(Agent):
    # tree manager, trimmer and grower - independent of tree structure
    type: Literal["overseer"] = "overseer"
    available_tools = overseer_toolset

    def _generate_prompt(self):
        return (
            f"{overseer_system_prompt}\n\n"
            f"{self._chats_part()}\n\n"
            f"{self._log_part()}\n\n"
            f"{self._task_part()}"
        )
