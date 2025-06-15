FROM debian:bookworm-slim
RUN apt-get update &&  \
    apt-get install -y apt-utils bash git iputils-ping curl wget zip unzip tar gzip bzip2 xz-utils python3 python-is-python3 nodejs npm &&  \
    rm -rf /var/lib/apt/lists/*
CMD ["/bin/bash"]