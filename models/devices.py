from typing import Literal


class Environment:
    # internal
    # defines a broad feature requiring
    device: Literal["browser", "linux"]


class VirtualDevice:
    # defines connection to an atomic part of a broader system, e.g.: linux_shell
    kind: Literal["text_file", "file_tree", "browser", "webpage", "linux_shell"]
    environment: Environment  # ref to shared env
