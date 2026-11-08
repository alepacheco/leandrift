# LeanDrift's image: git, Python 3 and elan. Lean toolchains are installed by elan on first use,
# into /opt/elan (mount a volume there to keep them between runs); Mathlib's cache goes to /cache.
FROM debian:trixie-slim

ARG ELAN_VERSION=v4.2.4
ARG TARGETARCH
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl git python3 \
 && rm -rf /var/lib/apt/lists/*
RUN set -e; \
    case "${TARGETARCH:-amd64}" in \
      amd64) triple=x86_64-unknown-linux-gnu; sum=42b94d4244e8353142c456ec0e4ca6528fd898a6c604d4059f494e706e431f63 ;; \
      arm64) triple=aarch64-unknown-linux-gnu; sum=05febd124d84ebf994b2e7479922a5650b1e950c17ae3bd1ddd776b65bb72bf9 ;; \
      *) echo "unsupported architecture ${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    curl -fsSL -o /tmp/elan.tar.gz "https://github.com/leanprover/elan/releases/download/${ELAN_VERSION}/elan-${triple}.tar.gz"; \
    echo "${sum}  /tmp/elan.tar.gz" | sha256sum -c -; \
    tar -xzf /tmp/elan.tar.gz -C /tmp; \
    ELAN_HOME=/opt/elan /tmp/elan-init -y --no-modify-path --default-toolchain none; \
    rm /tmp/elan-init /tmp/elan.tar.gz; \
    chmod -R a+rwX /opt/elan
ENV ELAN_HOME=/opt/elan
ENV PATH=/opt/elan/bin:$PATH
# Mathlib's prebuilt cache, and a work directory, writable by any user.
RUN mkdir -p /cache /work && chmod 1777 /cache /work
ENV XDG_CACHE_HOME=/cache

COPY . /opt/leandrift
ENV PATH=/opt/leandrift/bin:$PATH
WORKDIR /work
