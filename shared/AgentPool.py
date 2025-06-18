from typing import Any

from langchain_core.messages import AIMessage, HumanMessage


class AgentPool:
    _instance = None

    def _init(self):
        # runtime importing - resolves circular dependencies
        # fixme: this is hacky - rewrite Pool as generic, type as [Agent] and pass to each Agent
        from models.agents.base import Agent

        self._store: dict[str, Agent] = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def register(self, agent_id, agent: Any):
        # note: could move creation here if we moved methods out of Agent
        self._store[agent_id] = agent

    def get(self, agent_id):
        return self._store.get(agent_id)

    def remove(self, agent_id):
        return self._store.pop(agent_id)

    def execute(self, agent_id):
        return self.get(agent_id).run_turn()

    def message(self, from_id, to_id, message):
        sender = self.get(from_id)
        receiver = self.get(to_id)

        if sender is None or receiver is None:
            raise RuntimeError(f"Invalid sender/receiver: {sender}/{receiver}")

        sender_chat = sender.external_chats.get(to_id)
        receiver_chat = receiver.external_chats.get(from_id)

        if sender_chat is None or receiver_chat is None:
            raise RuntimeError("No link between sender & receiver.")

        receiver.queue_response(sender.id)

        sender_chat.chat_history.append(AIMessage(message))
        receiver_chat.chat_history.append(HumanMessage(message))
