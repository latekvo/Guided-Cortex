from typing import Literal

from langchain_core.tools import tool

from models.agents.base import Agent
from prompts.worker import worker_system_prompt


class Worker(Agent):
    @tool
    def submit_work(self, work_result: str):
        """Submit your work once the work is high quality and working well."""
        pass

    @tool
    def run_linux_shell_command(self, command: str):
        """Runs a linux shell command."""
        pass

    @tool
    def write_to_scratchpad(self, command: str):
        """Writes a tiny note to your low-capacity scratchpad."""
        # Scratchpad is provided to workers, as their time is abundant and their context is disposable.
        # Worker tasks may also turn out more complex than expected, we don't want this to cause excessive
        # communications with the worker's parent, as it's unlikely they'd find a good solution together.
        pass

    # tree leaf - access to practical tools
    type: Literal["worker"] = "worker"
    # devices: list[VirtualDevice] # device system which extends available tooling, overkill for now

    def __init__(self, task):
        super().__init__(task)
        self.available_tools += [
            self.submit_work,
            self.run_linux_shell_command,
            self.write_to_scratchpad,
        ]

    def _generate_prompt(self):
        return (
            f"{worker_system_prompt}\n\n"
            f"{self._chats_part()}\n\n"
            f"{self._log_part()}\n\n"
            f"{self._task_part()}"
        )
