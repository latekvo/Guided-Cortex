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
from langchain_core.tools import BaseTool
from langchain_core.tools import tool
from pydantic import ValidationError

from models.chats import ExternalChat
from shared.CoreLLM import CoreLLM


# All functions HAVE to be defined within the agent classes.
# This is the simplest way for them to interact with the hierarchy and agent-specific props.

# We want to add 'reasoning' to each tool call.
# Do we have to convert the tools to structural outputs?
# As a hack, could just add `_reasoning: str` tool arg.


class Agent(ABC):
    @tool
    def broadcast_question(self, question: str):
        """Broadcasts a question within your team, opens a chat with the peer who can answer you."""
        # overseer determines if the question can and should be answered, then routes it appropriately
        pass

    @tool
    def message_peer(self, message: str, peer_id: str):
        """Sends a message in one of your open peer chats."""
        # opens communication with an agent relevant to request
        # we have to limit possible connections, they may eat up context
        pass

    @tool
    def close_peer_chat(self, peer_id: str):
        """Closes a chat once the original question has been resolved."""
        pass

    @tool
    def message_superior(self, message: str):
        """Sends message to your superior."""
        # direct communication with parent
        pass

    id: str  # unique but readable, max 8 base36 chars
    label: str  # non-unique
    type: Literal["overseer", "manager", "worker", "verifier"]

    creation_task: str
    available_tools: list[BaseTool]
    interface_chat: list[BaseMessage]  # action history, tool calls, UI & notes
    external_chats: list[ExternalChat]  # chats opened with other agents

    llm: BaseChatModel  # ref to predefined class
    token_limit: int  # todo: implement

    def __init__(self, task: str, label: str):
        self.llm = CoreLLM()
        self.id = uuid4().hex[:6]  # todo: collision avoidance, collisions likely
        self.label = label
        self.creation_task = task
        self.interface_chat = []
        self.external_chats = []
        self.available_tools = [
            self.broadcast_question,
            self.message_peer,
            self.close_peer_chat,
            self.message_superior,
        ]

    def _get_chat_by_member_id(self, member_id) -> ExternalChat | None:
        for chat in self.external_chats:
            if chat.target_id == member_id or chat.initiator_id == member_id:
                return chat

    def _task_part(self):
        return f"# YOUR PRIMARY OBJECTIVE: {self.creation_task}\n\n"

    def _chats_part(self):
        # todo: show last N messages (dynamically adjust N probably)
        chats_str = ""
        for chat in self.external_chats:
            if chat.initiator_id == self.id:
                other_id = chat.target_id
            else:
                other_id = chat.initiator_id
            # temporary placeholder, use actual labels
            peer_label = other_id
            chats_str += f"- Conversation with: {peer_label}, opening reason: {chat.opening_reason}\n"
        return f"# List of open conversations:\n" + chats_str

    def _log_part(self):
        chats_str = ""
        for msg in self.interface_chat:
            chats_str += f'> "{msg.name}": "{msg.content}"\n'
        return f"# Log of your actions:\n" + chats_str

    @abstractmethod
    def _generate_prompt(self):
        raise NotImplementedError()

    def _execute_tool_call(self, tool_call: ToolCall) -> ToolMessage:
        tools = {t.name: t for t in self.available_tools}
        t_id = tool_call["id"]
        t_name = tool_call["name"]
        t_args = tool_call["args"]

        t_response = ToolMessage(
            tool_call_id=t_id,
            name=t_name,
            content=f'Tool mistyped or unavailable: "{t_name}"',
        )

        if t_name not in tools:
            return t_response

        try:
            call_result = tools[t_name].invoke(t_args)
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

    def run_turn(self):
        tool_llm = self.llm.bind_tools(self.available_tools)
        result = tool_llm.invoke(self._generate_prompt())
        # smart-cast to only possible output
        if isinstance(result, AIMessage):
            # todo: cram tool result back into self. stores
            if len(result.tool_calls) == 0:
                self.interface_chat.append(
                    SystemMessage(
                        "No tools were called. All non-tool input is ignored."
                    )
                )
            else:
                # todo: include both tool calls and tool results - interweave or stack them
                self.interface_chat.extend(self._execute_tool_calls(result.tool_calls))
