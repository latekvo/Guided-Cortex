from enum import Enum

from colorama import Fore, Back, Style


class Trace(Enum):
    # no simple way to convert front-color to back-color
    CHAT = (Fore.CYAN, Back.CYAN)
    DEL_CHAT = (Fore.RED, Back.RED)
    SHELL = (Fore.GREEN, Back.GREEN)
    THINK = (Fore.LIGHTYELLOW_EX, Back.LIGHTYELLOW_EX)
    TOOL = (Fore.LIGHTGREEN_EX, Back.LIGHTGREEN_EX)
    NEW_TASK = (Fore.BLUE, Back.BLUE)
    DEL_TASK = (Fore.LIGHTRED_EX, Back.LIGHTRED_EX)


def trace(kind: Trace, header: str, message: str = ""):
    trace_head = f"{kind.value[1]}  {Style.RESET_ALL}"
    trace_body = f"{kind.value[0]}{header}{Style.RESET_ALL}{message}"
    print(f"{trace_head} {trace_body}")
