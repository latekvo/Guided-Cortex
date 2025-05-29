import subprocess
from subprocess import Popen

# 1. `docker run` starts a runtime-persistent instance.
# 2. `docker exec` hooks an agent into the instance.
# Multiple Workers may be hooked in independently.

linux_instances: dict[str, Popen[str]] = {}

main_linux_instance = subprocess.Popen(
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


def use_linux_shell(command_text: str, instance_id: str) -> str | None:
    global linux_instances
    shell = linux_instances.get(instance_id)
    if shell is None:
        return None
    shell.stdin.write(command_text + "\n")
    shell.stdin.flush()
    # todo: handle multi-line output
    return shell.stdout.readline()


def is_linux_ok() -> bool:
    main_linux_instance.stdin.write("echo foo bar baz\n")
    main_linux_instance.stdin.flush()
    out = main_linux_instance.stdout.readline()
    err = main_linux_instance.stderr.readline()
    print("LINUX CHECK: out:", out)
    print("LINUX CHECK: err:", err)
    if out is None or out == "":
        return False
    return True


is_linux_ok()
