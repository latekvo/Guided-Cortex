from debug.visualizer import visualize_tree
from models.agents.general import General
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
    root_manager = General(USER_ID, "Execute the user's orders", "Team Lead")

    user_message = input("Write message to root AI: ")

    # fixme: Chats seem to be broken. Debug and fix.
    chat_for_self, chat_for_root = create_chat_pair(
        USER_ID,
        root_manager.id,
        user_message,
    )

    root_manager.external_chats[USER_ID] = chat_for_root

    while True:
        root_manager.run_turn_recurse()
        visualize_tree(root_manager)
        user_message = input("Press enter to skip. Write message to root AI: ")
        if user_message == "":
            continue
        chat_for_self.send_message(user_message)


main()
