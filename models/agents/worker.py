from typing import Literal

from models.agents.base import Agent


class Worker(Agent):
    # tree leaf - access to practical tools
    type: Literal["worker"] = "worker"
    # devices: list[VirtualDevice] # device system which extends available tooling, overkill for now

    def _generate_prompt(self):
        raise NotImplementedError()
