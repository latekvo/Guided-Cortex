from abc import ABC, abstractmethod
from typing import Literal
from uuid import uuid4

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    ToolCall,
    ToolMessage,
    SystemMessage,
)
from langchain_core.tools import BaseTool, StructuredTool
from pydantic import ValidationError

from debug.tracer import trace, Trace
from debug.viewer import serialize_prompt_view
from shared.AgentPool import AgentPool
from shared.CoreLLM import CoreLLM
from shared.ExternalChat import ExternalChat

# We want to add 'reasoning' to each tool call.
# Do we have to convert the tools to structural outputs?
# As a hack, could just add `_reasoning: str` tool arg.

# Note: ALL incoming messages are "Human", all generated messages are "AI"
#       This is necessary for the models to function correctly, to recognize themselves and others.

# What do we want the agent to see?
# 1. Primary goal - briefly
# 2. Detailed requirements list - instead of memory, let this be adjusted overtime
# 3. Detailed plan - and attach "Being executed by child XYZ" to each point
# Note: Having multiple chats is too confusing to the model
# Note: I think we can get away with not doing a primary model chat at all, or doing just 1/2 messages lookback

# Agents may fall into prolonged sleep.
# This is good, but may lead to stagnation.
# Nudge allows agents to occasionally wake up and check their surroundings.
ROUNDS_TO_NUDGE = 7
NUDGE_PROMPT = "Hey, just checking in on the progress."


class Agent(ABC):
    # def _tool_broadcast_question(self, _question: str):
    #     """Broadcasts a question within your team, opens a chat with the peer who can answer you."""
    #     # overseer determines if the question can and should be answered, then routes it appropriately
    #     return "Broadcasting questions is not possible yet."

    def _tool_send_message(self, message: str, target_id: str):
        if target_id not in self.external_chats:
            # New chats are opened only for special occasions, e.g. resolving conflicts.
            return f"Chat to {target_id} does not exist."
        trace(Trace.CHAT, f"[{self.label} -> {target_id}]: ", message)
        AgentPool().message(self.id, target_id, message)
        return "Message sent."

    def _tool_close_peer_chat(self, peer_id: str):
        if peer_id not in self.external_chats:
            return f"No chat with {peer_id} exists."
        if peer_id == self.parent_id:
            return "You cannot close the chat with your superior."
        trace(
            Trace.DEL_CHAT,
            f"[{self.label} -> {peer_id}]: ",
            "=== CLOSING PEER CHAT ===",
        )
        # todo: remove message from child, add __del__ to auto-resolve circ dep
        del self.external_chats[peer_id]
        return "Closed chat."

    def _tool_message_superior(self, message: str):
        trace(Trace.CHAT, f"[{self.label} -> {self.parent_id} (superior)]: ", message)
        AgentPool().message(self.id, self.parent_id, message)
        return "Message sent."

    id: str  # unique but readable, 6 alpha-num chars
    parent_id: str
    label: str  # non-unique
    type: Literal["overseer", "manager", "worker", "verifier"]

    creation_task: str
    _response_queue: list[str]  # queue of all agent ids pending a response
    _available_tools: list[BaseTool]

    # todo: ExternalChat should have direct member ref, but circ refs can be an issue for GC in some known situations.
    external_chats: dict[str, ExternalChat]  # chats opened with other agents

    llm: BaseChatModel  # ref to predefined class
    token_limit: int  # todo: implement

    # misc. optimizations
    idle_turns_count: int

    def __init__(self, parent_id: str, task: str, label: str):
        self.id = uuid4().hex[:6]  # todo: add collision avoidance, collisions likely
        AgentPool().register(self.id, self)
        self.llm = CoreLLM()
        self.parent_id = parent_id
        self.label = label
        self.creation_task = task
        self._response_queue = []
        self.external_chats = {}
        self.idle_turns_count = 0
        self._available_tools = [
            # todo: remove all communication tools - the tree agents should only act as project scaffold.
            #       the only reason why they'd need to talk to each other, is project interventions and corrections.
            #       ^ corrections should be offloaded to separate, off-tree agents.
            #       This way, in-tree agents don't have to deal with complexities of context switching.
            # todo: agent should:
            #       - sleep if it has children and no queued responses
            #       - work if it is has no children
            StructuredTool.from_function(
                name="send_message",
                func=self._tool_send_message,
                description="Sends a message to one of your open peer chats.",
            ),
            StructuredTool.from_function(
                name="close_peer_chat",
                func=self._tool_close_peer_chat,
                description="Closes a chat once the original question has been resolved.",
            ),
            StructuredTool.from_function(
                name="message_your_superior",
                func=self._tool_message_superior,
                description="Sends message to your superior.",
            ),
        ]

    def _get_chat_by_target_id(self, target_id) -> ExternalChat | None:
        return self.external_chats.get(target_id)

    def _task_part(self) -> SystemMessage:
        return SystemMessage(f"# Your primary objective: {self.creation_task}\n")

    def _chat_part(self, target_id: str) -> list[BaseMessage]:
        return [
            SystemMessage(f"Your chat with {target_id}:\n\n"),
            *self.external_chats.get(target_id).chat_history,
        ]

    def _sign_message(self, text: str):
        clean_text = text.replace("\n", "<br>")
        # Using JSONL, it's most likely the least confusing format for dense entries
        # Signed msgs should remain slim, recipient's details will be displayed separately
        return f'{{"author": "{self.id}", "message": "{clean_text}"}}\n'

    @abstractmethod
    def _generate_prompt(self, target_id: str) -> list[BaseMessage]:
        raise NotImplementedError()

    def _execute_tool_call(self, tool_call: ToolCall) -> ToolMessage:
        tools = {t.name: t for t in self._available_tools}
        t_id = tool_call["id"]
        t_name = tool_call["name"]
        t_args = tool_call["args"]

        # placeholder, will be copied to every tool definition
        trace(Trace.CHAT, f"{self.label} called {t_name}.", f" Args: {str(t_args)}")

        t_response = ToolMessage(
            tool_call_id=t_id,
            name=t_name,
            content=f'Tool mistyped or unavailable: "{t_name}"',
        )

        if t_name not in tools:
            return t_response

        try:
            call_result = tools[t_name].invoke(t_args)
            trace(Trace.TOOL, f"Tool {t_name}({t_args}) output:", call_result)
            t_response.content = str(call_result)
            return t_response
        except ValidationError:
            err = f"Tool called with invalid arguments, or invalid argument count."
            t_response.content = err
            return t_response

    def _execute_tool_calls(self, tool_calls: list[ToolCall]) -> list[ToolMessage]:
        t_results = []
        for tool_call in tool_calls:
            res = self._execute_tool_call(tool_call)
            t_results.append(res)
        return t_results

    def get_agent_view(self, target_id: str):
        prompt = self._generate_prompt(target_id)
        return serialize_prompt_view(prompt)

    def queue_response(self, respond_to_id: str):
        self._response_queue.append(respond_to_id)
        # keep deduped
        self._response_queue = list(set(self._response_queue))

    def _respond_to_target(self, target_id: str):
        # todo: handle errors better
        tool_llm = self.llm.bind_tools(self._available_tools).with_retry()

        result = tool_llm.invoke(self._generate_prompt(target_id))

        # smart-cast to only possible output
        if isinstance(result, AIMessage):
            AgentPool().message(self.id, target_id, result)

            # tool call results are saved to the chat local-side only
            target_chat = self.external_chats.get(target_id)
            t_results = self._execute_tool_calls(result.tool_calls)
            target_chat.chat_history.extend(t_results)
            if len(t_results) > 0:
                self.queue_response(target_id)

    def run_turn(self):
        if len(self._response_queue) == 0:
            self.idle_turns_count += 1
        if self.idle_turns_count == ROUNDS_TO_NUDGE:
            AgentPool().message(self.parent_id, self.id, NUDGE_PROMPT)
        for target_id in self._response_queue:
            self._respond_to_target(target_id)
            self.idle_turns_count = 0
        self._response_queue.clear()
