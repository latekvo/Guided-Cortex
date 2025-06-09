from typing import Literal

from langchain_core.messages import SystemMessage, BaseMessage, AIMessage
from langchain_core.tools import StructuredTool

from debug.tracer import Trace, trace
from models.agents.base import Agent
from models.chats import create_chat_pair
from prompts.general import general_system_prompt
from runtimes.runtime import use_linux_shell


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
        self.children.append(child)
        chat_for_self, chat_for_child = create_chat_pair(
            self.id,
            child.id,
            self.label,
            child.label,
            task_description,
            self.interface_chat,
            child.interface_chat,
        )
        self.external_chats |= {child.id: chat_for_self}
        child.external_chats |= {self.id: chat_for_child}
        return f"Task '{child.id}' created successfully."

    def _tool_accept_task_result(self, task_id: str):
        # Task completion notification is delivered via UI.
        # This function simply closes the task if it's in a satisfactory state.
        child = self._get_child_by_id(task_id)
        chat = self._get_chat_by_target_id(task_id)
        if child is None or chat is None:
            return f"Error: Task {task_id} not found."

        trace(
            Trace.DEL_TASK,
            f"{self.label} removes {child.label}: ",
            "Task has been completed.",
        )

        del child.external_chats[self.id].target_chat_ref  # circ dep
        del child.external_chats[self.id]
        del self.external_chats[child.id].target_chat_ref  # circ dep
        del self.external_chats[child.id]
        self.children.remove(child)
        return f"Task {task_id} closed as completed."

    def _tool_deny_task_result(self, task_id: str, denial_reason: str):
        # While generally active communication is preferred,
        # there could be a situation where invalid work is submitted and successfully verified.
        trace(Trace.CHAT, f"{self.label} denies {task_id}'s work result.")

        chat = self._get_chat_by_target_id(task_id)
        if chat is None:
            return f"Error: Task {task_id} not found."
        chat.send_message(f"NOTIFICATION: Task result has been denied: {denial_reason}")
        return "Task result denied. Notified worker about the denial reason."

    def _tool_terminate_worker(self, task_id: str):
        child = self._get_child_by_id(task_id)
        chat = self._get_chat_by_target_id(task_id)
        if child is None or chat is None:
            return f"Error: Task {task_id} not found."
        trace(Trace.DEL_TASK, f"{self.label} removes {child.label}")

        self.children.remove(child)
        del self.external_chats[child.id]
        return f"Task {task_id} successfully terminated."

    def _tool_skip_turn(self):
        trace(Trace.THINK, f"{self.label} skips turn.")
        return f"Turn skipped, passing time."

    def _tool_submit_work(self, work_result: str):
        # todo: submit_work should be dispatching a verifier.
        #       Right now, it just sends a message to its superior.
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
        self.scratchpad_chat.append(SystemMessage(f"## Scratchpad node:\n\n{text}"))
        return "Added entry to scratchpad."

    @staticmethod
    def _sleep_through_turn():
        return "Sleeping through this turn."

    # tree node - access to technical tools, dispatches subcontractors
    type: Literal["general"] = "general"
    children: list[Agent]
    scratchpad_chat: list[SystemMessage]  # notes

    def __init__(self, parent_id, task, label):
        super().__init__(parent_id, task, label)
        self.scratchpad_chat = []
        self.children = []
        self.available_tools += [
            StructuredTool.from_function(
                name="hire_worker",
                func=self._tool_hire_worker,
                description="Schedules creation and execution of the specified task. The label should be tiny, and the task description should be exhaustive.",
            ),
            StructuredTool.from_function(
                name="accept_task_result",
                func=self._tool_accept_task_result,
                description="Approve the work once it is high quality and working well.",
            ),
            StructuredTool.from_function(
                name="deny_task_result",
                func=self._tool_deny_task_result,
                description="Deny the work if it does not meet your use-case, requirements, or quality standards.",
            ),
            StructuredTool.from_function(
                name="terminate_worker",
                func=self._tool_terminate_worker,
                description="Stops task execution, whether it is finished or still executing.",
            ),
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
            StructuredTool.from_function(
                name="sleep_through_turn",
                func=self._sleep_through_turn,
                description="Skips your current turn until something happens. Use when got nothing better to do.",
            ),
        ]

    def _get_child_by_id(self, task_id) -> Agent | None:
        # todo: convert self.children to dict
        for child in self.children:
            if child.id == task_id:
                return child
        return None

    def run_turn_recurse(self):
        for child in self.children:
            if isinstance(child, General):
                child.run_turn_recurse()
            else:
                # Verifier or Overseer - these get the first turn to ensure back-to-back behaviour
                child.run_turn()
        self.run_turn()

    def _scratchpad_part(self) -> list[BaseMessage]:
        return [
            SystemMessage("# Your scratchpad:"),
            *self.scratchpad_chat,
        ]

    def _children_part(self) -> BaseMessage:
        out = "# List of your workers:\n\n"
        for child in self.children:
            child_task = child.creation_task.replace("\n", "<br>")
            out += f"- {child.label}, id: {child.id}, executing task: {child_task}\n"
        out += "\n"
        return SystemMessage(out)

    def _generate_prompt(self) -> list[BaseMessage]:
        return [
            SystemMessage(general_system_prompt),
            self._task_part(),
            *self._scratchpad_part(),  # todo: this might get lost too quick
            *self._chats_part(),
            # todo: add UI with all the children, todos, etc here
            *self._log_part(),
        ]
