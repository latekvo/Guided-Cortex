from typing import Literal

from models.agents.base import Agent


class Overseer(Agent):
    # tree manager, trimmer and grower - independent of tree structure
    type: Literal["overseer"] = "overseer"

    def _generate_prompt(self):
        raise NotImplementedError()
