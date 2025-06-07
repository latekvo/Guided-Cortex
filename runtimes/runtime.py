import subprocess
from subprocess import Popen, TimeoutExpired

# 1. `docker run` starts a runtime-persistent instance.
# 2. `docker exec` hooks an agent into the instance.
# Multiple Workers may be hooked in independently.

linux_instances: dict[str, Popen[str]] = {}

subprocess.run(
    [
        "docker",
        "run",
        "--rm",
        "-dit",
        "--network=none",
        "--cpus=0.5",
        "--memory=128m",
        "--cap-drop=ALL",
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
        ["docker", "exec", "-i", "linux-shell", "/bin/bash"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    linux_instances |= {instance_id: shell}


def delete_linux_instance(instance_id: str):
    linux_instances.pop(instance_id, None)


SHELL_DEFAULT_TIMEOUT = 10


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

    try:
        outs, errs = shell.communicate(command_text, timeout=timeout)
        return outs + errs
    except TimeoutExpired:
        shell.kill()
        return f"Timeout error: Command terminated after {timeout} seconds."


def is_linux_ok() -> bool:
    create_linux_instance("__test")
    out = use_linux_shell('echo "OK"', "__test")
    if out is None or out == "":
        print("LINUX CHECK:", "FAILED")
        return False
    print("LINUX CHECK:", out)
    return True
