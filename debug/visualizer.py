from models.agents.base import Agent
from models.agents.general import General


def visualize_tree(root: Agent, indent=0):
    print(" " * indent + f"- [{root.type}] {root.label}")
    if isinstance(root, General):
        for child in root.children.values():
            visualize_tree(child, indent + 1)
