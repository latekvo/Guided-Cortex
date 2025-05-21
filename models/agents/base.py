from typing import Literal

from langchain_core.language_models import BaseLLM
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool

from models.chats import ExternalChat


class Agent:
    id: str  # unique but readable, max 8 base36 chars
    label: str  # non-unique
    type: Literal["overseer", "manager", "worker", "verifier"]

    available_tools: list[BaseTool]
    interface_chat: list[BaseMessage]  # tool calls, UI & notes
    external_chats: list[ExternalChat]  # chats opened with other agents

    # metadata
    task: str
    system_prompt: str
    llm: BaseLLM  # ref to predefined class

    def run_turn(self):
        pass
