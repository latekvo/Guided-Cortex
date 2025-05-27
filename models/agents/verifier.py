from typing import Literal

from models.agents.base import Agent
from prompts.verifier import verifier_system_prompt
from tools.verifier import verifier_toolset


class Verifier(Agent):
    # tree leaf - ensures validity and quality of worker's output before sending it over to the manager
    type: Literal["verifier"] = "verifier"
    available_tools = verifier_toolset

    def _generate_prompt(self):
        return (
            f"{verifier_system_prompt}\n\n"
            f"{self._chats_part()}\n\n"
            f"{self._log_part()}\n\n"
            f"{self._task_part()}"
        )
