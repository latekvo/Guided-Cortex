from colorama import Back, Style, Fore

from debug.visualizer import visualize_tree
from models.agents.general import General
from models.agents.user import User
from runtimes.runtime import is_linux_ok
from shared.AgentPool import AgentPool
from shared.logo import logo

# note: We're not doing any persistent thinking functions
#       Managers should be able to divide the tasks and respond to events,
#       anything more will clog up context. Answer-time reasoning should be enough.
#       Workers even more so, their tasks are all 1-turn + corrections hopefully,
#       a longer chain of though should be replaced by a deeper hierarchy where possible.

# note: there doesn't seem to be a need for an id-based pool of agents, thus sticking to a ref-tree


# todo: impl async user chat or injection CLI
#       user should be able to contact ANY member of the hierarchy


SECTION_SEP = f"{Fore.LIGHTRED_EX}{Back.LIGHTWHITE_EX}-------------------------------{Style.RESET_ALL}"
INPUT_MSG = f"{Back.YELLOW}Write message to root AI:{Style.RESET_ALL} "

# todo: add retry conditions to tools, retry response on said fail


def main():
    is_linux_ok()
    user_agent = User()
    root_manager = General(user_agent.id, "Execute the user's orders", "Team Lead")

    user_agent.connect_to(root_manager.id)

    print(logo)

    message = input(INPUT_MSG)
    AgentPool().message(user_agent.id, root_manager.id, message)

    while True:
        root_manager.run_turn_recurse()
        visualize_tree(root_manager)
        print(SECTION_SEP)
        print(root_manager.get_agent_view(user_agent.id))
        print(SECTION_SEP)
        message = input(f"{Back.YELLOW}Press enter to skip. {INPUT_MSG}")
        print(SECTION_SEP)
        if message == "":
            continue
        AgentPool().message(user_agent.id, root_manager.id, message)


main()
