# syntax=docker/dockerfile:1

ARG PYTHON_IMAGE=python:3.14-slim-bookworm
ARG NODE_IMAGE=node:24.12-bookworm-slim

# -----------------------------------------------------------------------------
# Shared Node.js toolchain
# -----------------------------------------------------------------------------
FROM ${NODE_IMAGE} AS node_toolchain


# -----------------------------------------------------------------------------
# check
# -----------------------------------------------------------------------------
FROM ${PYTHON_IMAGE} AS check

RUN apt-get update \
    && apt-get install --yes --no-install-recommends bash ca-certificates \
    && rm -rf /var/lib/apt/lists/*


COPY --from=node_toolchain /usr/local/bin/ /usr/local/bin/
COPY --from=node_toolchain /usr/local/lib/node_modules/ /usr/local/lib/node_modules/

WORKDIR /src

COPY int/requirements.txt /tmp/int-requirements.txt
RUN python -m venv /opt/check-python \
    && /opt/check-python/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/check-python/bin/pip install --no-cache-dir -r /tmp/int-requirements.txt \
    && /opt/check-python/bin/pip install --no-cache-dir \
        "ruff~=0.14.4" \
        "mypy~=1.19.1" \
        "types-lxml>=2026.2.16" \
    && rm -f /tmp/int-requirements.txt


RUN mkdir -p /src/int /src/tester /usr/local/lib/ipp
COPY <<'JSON' /src/package.json
{
  "name": "ipp26-check-tools",
  "private": true,
  "type": "module",
  "devDependencies": {
    "@eslint/js": "~9.32.0",
    "@types/node": "~24.10.0",
    "eslint": "~9.32.0",
    "prettier": "~3.7.0",
    "typescript": "~5.9.0",
    "typescript-eslint": "~8.52.0"
  }
}
JSON
RUN npm install --prefix /src --no-fund --no-audit

RUN ln -s /opt/check-python/bin/ruff /usr/local/bin/ruff-real \
    && ln -s /opt/check-python/bin/mypy /usr/local/bin/mypy-real \
    && ln -s /src/node_modules/.bin/eslint /usr/local/bin/eslint-real \
    && ln -s /src/node_modules/.bin/prettier /usr/local/bin/prettier-real

COPY <<'BASH' /usr/local/lib/ipp/check-shell-init.sh
#!/bin/bash
set -euo pipefail

link_tool() {
    local directory="$1"
    local link_name="$2"
    local target="$3"

    if [[ -d "$directory" ]]; then
        ln -snf "$target" "$directory/$link_name"
    fi
}

link_tool /src/int ruff /usr/local/bin/ruff-real
link_tool /src/int mypy /usr/local/bin/mypy-real
link_tool /src/tester eslint /usr/local/bin/eslint-real
link_tool /src/tester prettier /usr/local/bin/prettier-real
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
RUN npm ci

COPY tester/tsconfig.json ./
COPY tester/src/ ./src/
RUN npm run build


# -----------------------------------------------------------------------------
# runtime
# -----------------------------------------------------------------------------
FROM ${PYTHON_IMAGE} AS runtime

ENV VIRTUAL_ENV=/opt/runtime-python
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

WORKDIR /app

COPY int/requirements.txt /tmp/int-requirements.txt
RUN python -m venv "${VIRTUAL_ENV}" \
    && "${VIRTUAL_ENV}/bin/pip" install --no-cache-dir --upgrade pip \
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

COPY --from=node_toolchain /usr/local/bin/ /usr/local/bin/
COPY --from=node_toolchain /usr/local/lib/node_modules/ /usr/local/lib/node_modules/

WORKDIR /app/tester

COPY tester/package.json tester/package-lock.json ./
RUN npm ci --omit=dev --no-fund --no-audit

COPY --from=build-test /work/tester/dist ./dist

ENV SOL26_INTERPRETER=/usr/local/bin/solint

ENTRYPOINT ["node", "/app/tester/dist/tester.js"]