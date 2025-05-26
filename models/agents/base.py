from abc import ABC, abstractmethod
from typing import Literal

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, ToolCall, ToolMessage
from langchain_core.tools import BaseTool
from pydantic import ValidationError

from models.chats import ExternalChat


class Agent(ABC):
    id: str  # unique but readable, max 8 base36 chars
    label: str  # non-unique
    type: Literal["overseer", "manager", "worker", "verifier"]

    creation_task: str
    available_tools: list[BaseTool]
    interface_chat: list[BaseMessage]  # action history, tool calls, UI & notes
    external_chats: list[ExternalChat]  # chats opened with other agents

    # metadata
    llm: BaseChatModel  # ref to predefined class
    token_limit: int

    @abstractmethod
    def _generate_prompt(self):
        raise NotImplementedError()

    def _execute_tool_call(self, tool_call: ToolCall) -> ToolMessage:
        tools = {tool.name: tool for tool in self.available_tools}
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
        if len(tool_calls) == 0:
            return [ToolMessage("No tools were called. All non-tool input is ignored.")]
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
            self._execute_tool_calls(result.tool_calls)
