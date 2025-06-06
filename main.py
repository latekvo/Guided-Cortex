from debug.visualizer import visualize_tree
from models.agents.manager import Manager
from models.chats import create_chat_pair
from runtimes.runtime import is_linux_ok

# note: We're not doing any persistent thinking functions
#       Managers should be able to divide the tasks and respond to events,
#       anything more will clog up context. Answer-time reasoning should be enough.
#       Workers even more so, their tasks are all 1-turn + corrections hopefully,
#       a longer chain of though should be replaced by a deeper hierarchy where possible.

# note: there doesn't seem to be a need for an id-based pool of agents, thus sticking to a ref-tree


# todo: impl async user chat or injection CLI
#       user should be able to contact ANY member of the hierarchy

USER_ID = "ROOT_USER"

# todo: add mock UserAgent for injecting user into the tree


def main():
    is_linux_ok()
    root_manager = Manager(USER_ID, "Execute the user's orders", "Chief Director")

    chat_for_self, chat_for_root = create_chat_pair(
        USER_ID,
        root_manager.id,
        'Create 2 tasks with the following command "output Hello world"',
    )

    root_manager.external_chats[USER_ID] = chat_for_root

    root_manager.run_turn_recurse()
    visualize_tree(root_manager)


main()
