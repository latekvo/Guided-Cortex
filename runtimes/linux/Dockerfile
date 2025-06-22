FROM debian:bookworm-slim
RUN apt-get update &&  \
    apt-get install -y \
    apt-utils iputils-ping sudo tree \
    bash git curl wget \
    zip unzip tar gzip bzip2 xz-utils \
    python3 python-is-python3 python3-pip nodejs npm && \
    rm -rf /var/lib/apt/lists/*

# todo: alias vim & nano with `echo "You may not use text editors. Use echo instead."`
# todo: implement diff-based editor interface for the agents
# todo: alias `npx` to `yes | npx`

# Enable passwordless sudo
RUN useradd -m ai && \
    usermod -aG sudo ai && \
    echo 'ai ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/nopasswd && \
    chmod 440 /etc/sudoers.d/nopasswd

USER ai
CMD ["/bin/bash"]