# syntax=docker/dockerfile:1

ARG PYTHON_IMAGE=python:3.14-slim-bookworm
ARG NODE_IMAGE=node:24.12-bookworm-slim

# -----------------------------------------------------------------------------
# Shared Node.js toolchain
# -----------------------------------------------------------------------------
FROM ${NODE_IMAGE} AS node_toolchain


# -----------------------------------------------------------------------------
# check - this part was partially fixed using ai https://chatgpt.com/share/69bd37e6-cbe8-800b-a49e-5a0c5fa9e513 here, before there was an issue regarding not reading dependencies for typescript
# ai fix didnt fully work so i had to change it but the whole idea is not mine
# -----------------------------------------------------------------------------
FROM ${PYTHON_IMAGE} AS check

ENV VIRTUAL_ENV=/opt/check-python
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"
RUN apt-get update \
    && apt-get install --yes --no-install-recommends bash ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=node_toolchain /usr/local/bin/ /usr/local/bin/
COPY --from=node_toolchain /usr/local/lib/node_modules/ /usr/local/lib/node_modules/

WORKDIR /src

COPY int/requirements.txt /tmp/int-requirements.txt
COPY int/requirements-dev.txt /tmp/int-requirements-dev.txt
RUN python -m venv "${VIRTUAL_ENV}" \
    && "${VIRTUAL_ENV}/bin/pip" install --no-cache-dir \
        -r /tmp/int-requirements.txt \
        -r /tmp/int-requirements-dev.txt \
    && rm -f /tmp/int-requirements.txt /tmp/int-requirements-dev.txt

COPY tester/package.json /src/package.json
COPY tester/package-lock.json /src/package-lock.json
RUN npm ci --prefix /src --no-fund --no-audit

RUN mkdir -p /src/int /src/tester /usr/local/lib/ipp

COPY <<'BASH' /usr/local/lib/ipp/check-shell-init.sh
#!/bin/bash
set -euo pipefail

export VIRTUAL_ENV="${VIRTUAL_ENV:-/opt/check-python}"
export PATH="${VIRTUAL_ENV}/bin:${PATH}"
hash -r

link_tool() {
    local directory="$1"
    local link_name="$2"
    local target="$3"

    if [[ -d "$directory" ]]; then
        ln -sfn "$target" "$directory/$link_name"
    fi
}

link_tool /src/int ruff "${VIRTUAL_ENV}/bin/ruff"
link_tool /src/int mypy "${VIRTUAL_ENV}/bin/mypy"

link_tool /src/tester eslint /src/node_modules/.bin/eslint
link_tool /src/tester prettier /src/node_modules/.bin/prettier
link_tool /src/tester tsc /src/node_modules/.bin/tsc
BASH

RUN chmod +x /usr/local/lib/ipp/check-shell-init.sh \
    && printf '\nsource /usr/local/lib/ipp/check-shell-init.sh\n' >> /root/.bashrc

ENV BASH_ENV=/usr/local/lib/ipp/check-shell-init.sh
ENTRYPOINT ["/bin/bash"]


# -----------------------------------------------------------------------------
# build-test
# -----------------------------------------------------------------------------
FROM ${NODE_IMAGE} AS build-test

WORKDIR /work/tester

COPY tester/package.json tester/package-lock.json ./
RUN npm ci --no-fund --no-audit

COPY tester/tsconfig.json ./
COPY tester/src/ ./src/
RUN npm run build


# -----------------------------------------------------------------------------
# tester-runtime-deps
# -----------------------------------------------------------------------------
FROM ${NODE_IMAGE} AS tester-runtime-deps

WORKDIR /work/tester

COPY tester/package.json tester/package-lock.json ./
RUN npm ci --omit=dev --no-fund --no-audit


# -----------------------------------------------------------------------------
# runtime
# -----------------------------------------------------------------------------
FROM ${PYTHON_IMAGE} AS runtime

ENV VIRTUAL_ENV=/opt/runtime-python
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

WORKDIR /app

COPY int/requirements.txt /tmp/int-requirements.txt
RUN python -m venv "${VIRTUAL_ENV}" \
    && "${VIRTUAL_ENV}/bin/pip" install --no-cache-dir -r /tmp/int-requirements.txt \
    && rm -f /tmp/int-requirements.txt

COPY int/src/ /app/int/src/

COPY <<'BASH' /usr/local/bin/solint
#!/bin/sh
exec /opt/runtime-python/bin/python /app/int/src/solint.py "$@"
BASH

RUN chmod +x /usr/local/bin/solint

ENTRYPOINT ["/usr/local/bin/solint"]


# -----------------------------------------------------------------------------
# test
# -----------------------------------------------------------------------------
FROM runtime AS test

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        build-essential \
        diffutils \
        libxml2-dev \
        libxslt1-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=node_toolchain /usr/local/bin/ /usr/local/bin/
COPY --from=node_toolchain /usr/local/lib/node_modules/ /usr/local/lib/node_modules/

WORKDIR /app/tester

COPY --from=tester-runtime-deps /work/tester/package.json ./package.json
COPY --from=tester-runtime-deps /work/tester/node_modules ./node_modules
COPY --from=build-test /work/tester/dist ./dist

COPY tester/tools/sol2xml ./tools/sol2xml

RUN /opt/runtime-python/bin/pip install --no-cache-dir -r /app/tester/tools/sol2xml/requirements.txt

ENV SOL26_INTERPRETER=/usr/local/bin/solint
ENV SOL26_COMPILER_PYTHON=/opt/runtime-python/bin/python
ENV SOL26_COMPILER_SCRIPT=/app/tester/tools/sol2xml/sol_to_xml.py

ENTRYPOINT ["node", "/app/tester/dist/tester.js"]