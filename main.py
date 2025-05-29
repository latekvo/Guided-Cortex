from models.agents.base import Agent
from models.agents.manager import Manager

# note: We're not doing any persistent thinking functions
#       Managers should be able to divide the tasks and respond to events,
#       anything more will clog up context. Answer-time reasoning should be enough.
#       Workers even more so, their tasks are all 1-turn + corrections hopefully,
#       a longer chain of though should be replaced by a deeper hierarchy where possible.

# note: there doesn't seem to be a need for an id-based pool of agents, thus sticking to a ref-tree


def visualize_tree(root: Agent, indent=0):
    print(" " * indent + f"- [{root.type}] {root.label}")
    if isinstance(root, Manager):
        for child in root.children:
            visualize_tree(child, indent + 1)


# todo: impl async user chat or injection CLI
#       user should be able to contact ANY member of the hierarchy


def main():
    root_manager = Manager("ROOT_USER", 'Say "Hello World"', "Chief Director")
    root_manager.run_turn_recurse()
    visualize_tree(root_manager)


main()
