FROM ubuntu:22.04
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      gawk wget git diffstat unzip texinfo gcc g++ build-essential chrpath socat cpio \
      python3 python3-pip python3-pexpect python3-git python3-jinja2 python3-subunit \
      xz-utils debianutils iputils-ping zstd liblz4-tool file locales libacl1 \
      ca-certificates bzip2 \
    && locale-gen en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

# Той самий UID/GID, що й у користувача раннера, щоб не було проблем з правами
ARG UID=1000
ARG GID=1000
RUN groupadd -o -g ${GID} builder && useradd -m -o -u ${UID} -g ${GID} builder
USER builder
