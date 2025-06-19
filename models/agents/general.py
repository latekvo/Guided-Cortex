from typing import Literal

from langchain_core.messages import SystemMessage, BaseMessage
from langchain_core.tools import StructuredTool

from debug.tracer import Trace, trace
from models.agents.base import Agent
from prompts.general import general_system_prompt
from prompts.tool_descriptions import (
    hire_worker_desc,
    kill_worker_desc,
    run_shell_desc,
    sleep_turn_desc,
    write_scratchpad_desc,
)
from runtimes.runtime import use_linux_shell, create_linux_instance
from shared.AgentPool import AgentPool
from shared.ExternalChat import create_chat_pair


# General is an all-purpose agent, capable of both managerial and technical tasks.
# The previous split-role model had issues with predicting the complexity of the given tasks,
# this one should be able to adapt to new challenges in the given tasks more easily.


class General(Agent):
    def _tool_hire_worker(
        self,
        worker_label: str,
        task_description: str,
    ):
        child = General(self.id, task_description, worker_label)
        trace(Trace.NEW_TASK, f'{self.label} creates child "{child.label}".')
        self.children[child.id] = child

        chat_for_self, chat_for_child = create_chat_pair(
            self.id,
            child.id,
            self.label,
            child.label,
        )

        self.external_chats[child.id] = chat_for_self
        child.external_chats[self.id] = chat_for_child

        AgentPool().message(self.id, child.id, task_description)

        return f"Task '{child.id}' created successfully."

    def _tool_terminate_worker(self, task_id: str):
        child = self.children.get(task_id)
        chat = self._get_chat_by_target_id(task_id)
        if child is None or chat is None:
            return f"Error: Task {task_id} not found."
        trace(Trace.DEL_TASK, f"{self.label} removes {child.label}")

        del self.children[child.id]
        del self.external_chats[child.id]
        return f"Task {task_id} successfully terminated."

    def _tool_run_linux_shell_command(self, command: str):
        trace(Trace.SHELL, f"{self.label} uses shell: ", command)
        return use_linux_shell(command, self.id)

    def _tool_save_to_memory(self, text: str):
        trace(Trace.THINK, f"{self.label} saves to memory: ", text)
        self.memory_notes.append(f"- {text}")
        return "Added entry to your memory."

    @staticmethod
    def _sleep_through_turn():
        return "Sleeping through this turn."

    # tree node - access to technical tools, dispatches subcontractors
    type: Literal["general"] = "general"
    children: dict[str, Agent]
    memory_notes: list[str]  # notes

    def __init__(self, parent_id, task, label):
        super().__init__(parent_id, task, label)
        create_linux_instance(self.id)
        self.memory_notes = []
        self.children = {}
        self._available_tools += [
            StructuredTool.from_function(
                name="hire_worker",
                func=self._tool_hire_worker,
                description=hire_worker_desc,
            ),
            StructuredTool.from_function(
                name="terminate_worker",
                func=self._tool_terminate_worker,
                description=kill_worker_desc,
            ),
            StructuredTool.from_function(
                name="run_linux_shell_command",
                func=self._tool_run_linux_shell_command,
                description=run_shell_desc,
            ),
            StructuredTool.from_function(
                name="write_to_scratchpad",
                func=self._tool_save_to_memory,
                description=write_scratchpad_desc,
            ),
            StructuredTool.from_function(
                name="sleep_through_turn",
                func=self._sleep_through_turn,
                description=sleep_turn_desc,
            ),
        ]

    def run_turn_recurse(self):
        for child in self.children.values():
            if isinstance(child, General):
                child.run_turn_recurse()
            else:
                # Verifier or Overseer - these get the first turn to ensure back-to-back behaviour
                child.run_turn()
        self.run_turn()

    def _memory_part(self) -> list[BaseMessage]:
        if len(self.memory_notes) == 0:
            return []
        out = "# Your dynamic memory:"
        for mem in self.memory_notes:
            out += f"{mem}\n"
        return [SystemMessage(out)]

    def _worker_status_part(self) -> list[SystemMessage]:
        if len(self.children) == 0:
            return []
        out = "# List of employees currently working for you:\n\n"
        for child in self.children.values():
            child_task = child.creation_task.replace("\n", "<br>")
            out += f"- {child.label} [id: {child.id}] is executing task: {child_task}\n"
        out += "\n"
        return [SystemMessage(out)]

    def _generate_prompt(self, target_id: str) -> list[BaseMessage]:
        # todo: change of plan, this has to be minimized, chat visibility on-demand, scratchpad 1-turn long
        #       instead of memory, we will only expand requirements, what else is there to remember?
        return [
            SystemMessage(general_system_prompt),
            self._task_part(),
            *self._memory_part(),
            *self._worker_status_part(),
            *self._chat_part(target_id),
        ]
