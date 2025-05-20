from typing import Literal

from langchain.agents import LLMSingleActionAgent
from langchain_core.language_models import BaseLLM
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool


# note: there doesn't seem to be a need for an id-based pool of agents, thus sticking to a ref-tree

class ExternalChat:
    initiator_id: str
    target_id: str
    opening_reason: str
    chat_summary: str
    chat_history: list[BaseMessage]

class Agent:
    id: str # unique but readable, max 8 base36 chars
    label: str # non-unique
    type: Literal['overseer', 'manager', 'worker']

    available_tools: list[BaseTool]
    interface_chat: list[BaseMessage] # tool calls, UI & notes
    external_chats: list[ExternalChat] # chats opened with other agents

    # metadata
    task: str
    system_prompt: str
    llm: BaseLLM # ref to predefined class

class Overseer(Agent):
    # tree manager, trimmer and grower - independent of tree structure
    type: Literal['overseer'] = 'overseer'


class Manager(Agent):
    # tree node - dispatches sub-managers and workers
    type: Literal['manager'] = 'manager'
    children: list


class Worker(Agent):
    # tree leaf - access to practical tools
    type: Literal['worker'] = 'worker'


def main():
    return

main()