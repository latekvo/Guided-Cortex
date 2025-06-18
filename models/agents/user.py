from langchain_core.messages import BaseMessage

from models.agents.base import Agent
from shared.AgentPool import AgentPool
from shared.ExternalChat import create_chat_pair


# User agent allows the user to inject themselves as part of the tree


class User(Agent):
    def _generate_prompt(self, target_id: str) -> list[BaseMessage]:
        return []

    def __init__(self):
        super().__init__("__none", "__none", "Root User")
        AgentPool().remove(self.id)
        self.id = "ROOT_USER"
        AgentPool().register(self.id, self)

    def connect_to(self, target_id):
        for_self, for_target = create_chat_pair(
            self.id,
            target_id,
            "The User",
            "Your target",
        )

        self.external_chats[target_id] = for_self
        AgentPool().get(target_id).external_chats[self.id] = for_target
