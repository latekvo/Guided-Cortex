FROM debian:bookworm-slim
RUN apt-get update &&  \
    apt-get install -y \
    apt-utils bash git iputils-ping curl wget zip unzip tar gzip bzip2 xz-utils sudo \
    python3 python-is-python3 python3-pip nodejs npm &&  \
    rm -rf /var/lib/apt/lists/*

# Enable passwordless sudo
RUN useradd -m ai && \
    usermod -aG sudo ai && \
    echo 'ai ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/nopasswd && \
    chmod 440 /etc/sudoers.d/nopasswd

USER ai
CMD ["/bin/bash"]