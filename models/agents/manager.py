from typing import Literal

from models.agents.base import Agent


class Manager(Agent):
    # tree node - dispatches sub-managers and workers
    type: Literal["manager"] = "manager"
    children: list[Agent] = []

    def _generate_prompt(self):
        raise NotImplementedError()

    def run_turn_recurse(self):
        # this is only an approximation of inverse bfs
        # the primary point is to execute all workers before the managers
        for child in self.children:
            if isinstance(child, Manager):
                child.run_turn_recurse()
            else:
                # Worker, verifier or overseer
                # verifiers and overseers may be children or peers of event initiators
                child.run_turn()
        self.run_turn()
