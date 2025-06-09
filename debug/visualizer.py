from models.agents.base import Agent
from models.agents.general import General
from models.agents.manager import Manager


def visualize_tree(root: Agent, indent=0):
    print(" " * indent + f"- [{root.type}] {root.label}")
    if isinstance(root, Manager) or isinstance(root, General):
        for child in root.children:
            visualize_tree(child, indent + 1)
