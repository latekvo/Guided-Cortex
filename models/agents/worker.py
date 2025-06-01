from typing import Literal

from langchain_core.messages import AIMessage
from langchain_core.tools import tool

from models.agents.base import Agent
from prompts.worker import worker_system_prompt
from runtimes.runtime import (
    create_linux_instance,
    delete_linux_instance,
    use_linux_shell,
)


class Worker(Agent):
    @tool
    def submit_work(self, work_result: str):
        """Submit your work once the work is high quality and working well."""
        # todo: submit_work should be dispatching a verifier.
        #       Right now, it just sends a message to the Manager.
        message = AIMessage(
            self._sign_message(f"Submitting task, please evaluate: {work_result}")
        )
        self.external_chats[self.parent_id].chat_history.append(message)
        return (
            "Your work has been successfully submitted. It's currently being verified."
        )

    @tool
    def run_linux_shell_command(self, command: str):
        """Runs a linux shell command."""
        return use_linux_shell(command, self.id)

    @tool
    def write_to_scratchpad(self, text: str):
        """Writes a tiny note to your low-capacity scratchpad."""
        # Scratchpad is provided to workers, as their time is abundant and their context is disposable.
        # Worker tasks may also turn out more complex than expected, we don't want this to cause excessive
        # communications with the worker's parent, as it's unlikely they'd find a good solution together.
        self.scratchpad_chat.append(AIMessage(text))
        return "Added entry to scratchpad."

    # tree leaf - access to practical tools
    type: Literal["worker"] = "worker"
    # devices: list[VirtualDevice] # device system which extends available tooling, overkill for now
    pause_initiative = False
    scratchpad_chat: list[AIMessage]  # action history, tool calls, UI & notes

    def __init__(self, parent_id, task, label):
        super().__init__(parent_id, task, label)
        create_linux_instance(self.id)
        self.scratchpad_chat = []
        self.available_tools += [
            self.submit_work,
            self.run_linux_shell_command,
            self.write_to_scratchpad,
        ]

    def __del__(self):
        delete_linux_instance(self.id)

    def run_turn(self):
        # todo: if no new messages, and currently being evaluated (paused), skip turn
        super().run_turn()

    def _generate_prompt(self):
        return (
            f"{worker_system_prompt}\n\n"
            f"{self._chats_part()}\n\n"
            f"{self._log_part()}\n\n"
            f"{self._task_part()}"
        )
