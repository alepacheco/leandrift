# LeanDrift's build image: git, Python 3 and elan. Lean toolchains are installed by elan on first use,
# into $ELAN_HOME (mount a volume there to keep them between runs).
FROM debian:trixie-slim

ARG ELAN_VERSION=v4.2.4
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl git python3 \
 && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL "https://github.com/leanprover/elan/releases/download/${ELAN_VERSION}/elan-x86_64-unknown-linux-gnu.tar.gz" \
      | tar -xz -C /tmp \
 && ELAN_HOME=/opt/elan /tmp/elan-init -y --no-modify-path --default-toolchain none \
 && rm /tmp/elan-init \
 && chmod -R a+rwX /opt/elan
ENV ELAN_HOME=/opt/elan
ENV PATH=/opt/elan/bin:$PATH

COPY . /opt/leandrift
ENV PATH=/opt/leandrift/bin:$PATH
WORKDIR /work
