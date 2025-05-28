from typing import Literal

from langchain_core.tools import tool

from models.agents.base import Agent
from prompts.verifier import verifier_system_prompt


class Verifier(Agent):
    @tool
    def approve_work(self, optional_comment: str):
        """Approve the work once it is high quality and working well."""
        pass

    @tool
    def request_changes(self, requested_changes: str):
        """Reports all issues found within the proposed work, requests their improvement."""
        pass

    # tree leaf - ensures validity and quality of worker's output before sending it over to the manager
    type: Literal["verifier"] = "verifier"

    def __init__(self, task, label):
        super().__init__(task, label)
        self.available_tools += [
            self.approve_work,
            self.request_changes,
        ]

    def _generate_prompt(self):
        return (
            f"{verifier_system_prompt}\n\n"
            f"{self._chats_part()}\n\n"
            f"{self._log_part()}\n\n"
            f"{self._task_part()}"
        )
