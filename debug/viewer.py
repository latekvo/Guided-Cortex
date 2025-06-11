from colorama import Fore, Style
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    SystemMessage,
    HumanMessage,
    ToolMessage,
)

SYSTEM_MARK = Fore.WHITE
AI_MARK = Fore.CYAN
HUMAN_MARK = Fore.GREEN
TOOL_MARK = Fore.YELLOW


def serialize_prompt_view(messages: list[BaseMessage]):
    out = ""
    for message in messages:
        if isinstance(message, SystemMessage):
            out += SYSTEM_MARK
        elif isinstance(message, AIMessage):
            out += AI_MARK
        elif isinstance(message, HumanMessage):
            out += HUMAN_MARK
        elif isinstance(message, ToolMessage):
            out += HUMAN_MARK
        out += f"{message.content}{Style.RESET_ALL}"
    return out
