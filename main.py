from models.agents.manager import Manager

# note: We're not doing any persistent thinking functions
#       Managers should be able to divide the tasks and respond to events,
#       anything more will clog up context. Answer-time reasoning should be enough.
#       Workers even more so, their tasks are all 1-turn + corrections hopefully,
#       a longer chain of though should be replaced by a deeper hierarchy where possible.

# note: there doesn't seem to be a need for an id-based pool of agents, thus sticking to a ref-tree


root_manager = Manager('Say "Hello World"')


def main():
    root_manager.run_turn_recurse()
    return


main()
