import os
import subprocess
from subprocess import Popen, TimeoutExpired

# 1. `docker run` starts a runtime-persistent instance.
# 2. `docker exec` hooks an agent into the instance.
# Multiple Workers may be hooked in independently.

linux_instances: dict[str, Popen[str]] = {}

local_workspace_dir = os.path.abspath("workspace")

os.makedirs(local_workspace_dir, exist_ok=True)

subprocess.run(
    [
        "docker",
        "run",
        "--rm",
        "-dit",
        "-v",  # mounts fs locally
        f"{local_workspace_dir}:/home/ai",
        # "--network=none",  # disabled network
        "--network=bridge",  # enabled network
        "--cpus=0.5",
        "--memory=128m",
        # "--cap-drop=ALL", # safety, blocks multiple kernel capabilities (e.g. network)
        "--name",
        "linux-shell",
        "linux",
    ],
    # Args theoretically redundant due to main never being used.
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1,
)


def create_linux_instance(instance_id: str):
    global linux_instances
    shell = subprocess.Popen(
        [
            "docker",
            "exec",
            "-i",
            "-w",  # use home dir
            "/home/ai",
            "linux-shell",
            "/bin/bash",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    linux_instances[instance_id] = shell


def delete_linux_instance(instance_id: str):
    linux_instances.pop(instance_id, None)


# todo:
#  - Make all shell usages explicitly blocking & async
#  - Then, raise timeout to something like 15 minutes - allows for builds, installs, compilations.
SHELL_DEFAULT_TIMEOUT = 120


def use_linux_shell(
    command_text: str,
    instance_id: str,
    timeout_seconds: int = None,
) -> str | None:
    global linux_instances
    shell = linux_instances.get(instance_id)
    if shell is None:
        return None
    timeout = timeout_seconds or SHELL_DEFAULT_TIMEOUT

    # fixme: there is no shell persistence (e.g. cd doesn't work)
    # fixme: this is a quick patch to fix .communicate crashes
    create_linux_instance(instance_id)

    try:
        outs, errs = shell.communicate(command_text, timeout=timeout)
        return outs + errs
    except TimeoutExpired:
        shell.kill()
        return f"Timeout error: Command terminated after {timeout} seconds."


def get_project_tree() -> str | None:
    create_linux_instance("__tree")
    exclude_list = "|".join(["bin", "lib", "node_modules", "dist"])
    exclude_arg = f'"{exclude_list}"'
    return use_linux_shell(f"tree -I {exclude_arg}", "__tree")


TEST_CMD_ECHO = 'echo "OK"'
TEST_CMD_NET = "ping -c 1 -W 1 8.8.8.8 &> /dev/null && echo OK || echo NOT OK"


def is_linux_ok() -> bool:
    create_linux_instance("__test")

    echo_out = use_linux_shell(TEST_CMD_ECHO, "__test").strip()
    net_out = use_linux_shell(TEST_CMD_NET, "__test").strip()

    echo_ok = echo_out is not None and echo_out != ""
    net_ok = net_out is not None and net_out != ""

    if echo_ok:
        print(f"LINUX [HEALTH] CHECK: {echo_out}")
    else:
        print("LINUX [HEALTH] CHECK: FAILED")
        return False

    if net_ok:
        print(f"LINUX [NETWORK] CHECK: {net_out}")
    else:
        print("LINUX [NETWORK] CHECK: FAILED")
        return False

    return True
