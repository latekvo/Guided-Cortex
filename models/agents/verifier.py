from typing import Literal

from models.agents.base import Agent


class Verifier(Agent):
    # tree leaf - ensures validity and quality of worker's output before sending it over to the manager
    type: Literal["verifier"] = "verifier"
