from colorama import Fore, Style, Back
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

LB = Back.LIGHTBLACK_EX
PART_SEP = f"{Style.RESET_ALL}  {LB} end {Style.RESET_ALL}\n"


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
            out += TOOL_MARK
        out += f"{message.content}"
        if isinstance(message, AIMessage):
            for tool_call in message.tool_calls:
                t_name = tool_call["name"]
                t_args = tool_call["args"]
                out += f"\n- [tool call]: {t_name}({t_args})"
        out += f"{Style.RESET_ALL}{PART_SEP}"
    return out
