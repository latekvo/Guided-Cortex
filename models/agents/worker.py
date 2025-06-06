from typing import Literal

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from langchain_core.tools import StructuredTool

from debug.tracer import trace, Trace
from models.agents.base import Agent
from prompts.worker import worker_system_prompt
from runtimes.runtime import (
    create_linux_instance,
    delete_linux_instance,
    use_linux_shell,
)


class Worker(Agent):
    def _tool_submit_work(self, work_result: str):
        # todo: submit_work should be dispatching a verifier.
        #       Right now, it just sends a message to the Manager.
        trace(Trace.NEW_TASK, f"{self.label} submits work: ", work_result)

        message = AIMessage(
            self._sign_message(f"Submitting task, please evaluate: {work_result}")
        )
        self.external_chats[self.parent_id].chat_history.append(message)
        return (
            "Your work has been successfully submitted. It's currently being verified."
        )

    def _tool_run_linux_shell_command(self, command: str):
        trace(Trace.SHELL, f"{self.label} uses shell: ", command)
        return use_linux_shell(command, self.id)

    def _tool_write_to_scratchpad(self, text: str):
        # Scratchpad is provided to workers, as their time is abundant and their context is disposable.
        # Worker tasks may also turn out more complex than expected, we don't want this to cause excessive
        # communications with the worker's parent, as it's unlikely they'd find a good solution together.
        trace(Trace.THINK, f"{self.label} uses scratchpad: ", text)
        self.scratchpad_chat.append(AIMessage(text))
        return "Added entry to scratchpad."

    # tree leaf - access to practical tools
    type: Literal["worker"] = "worker"
    pause_initiative = False
    scratchpad_chat: list[AIMessage]  # action history, tool calls, UI & notes

    def __init__(self, parent_id, task, label):
        super().__init__(parent_id, task, label)
        create_linux_instance(self.id)
        self.scratchpad_chat = []
        self.available_tools += [
            StructuredTool.from_function(
                name="submit_work",
                func=self._tool_submit_work,
                description="Submit your work once the work is high quality and working well.",
            ),
            StructuredTool.from_function(
                name="run_linux_shell_command",
                func=self._tool_run_linux_shell_command,
                description="Runs a linux shell command.",
            ),
            StructuredTool.from_function(
                name="write_to_scratchpad",
                func=self._tool_write_to_scratchpad,
                description="Writes a tiny note to your low-capacity scratchpad.",
            ),
        ]

    def __del__(self):
        delete_linux_instance(self.id)

    def run_turn(self):
        # todo: if no new messages, and currently being evaluated (paused), skip turn
        super().run_turn()

    def _generate_prompt(self) -> list[BaseMessage]:
        return [
            SystemMessage(worker_system_prompt),
            self._task_part(),
            self._chats_part(),
            self._log_part(),
        ]
