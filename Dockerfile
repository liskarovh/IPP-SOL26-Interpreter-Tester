# syntax=docker/dockerfile:1

ARG PYTHON_IMAGE=python:3.14-bookworm
ARG NODE_IMAGE=node:24.12-bookworm

# -----------------------------------------------------------------------------
# Shared Node.js toolchain
# -----------------------------------------------------------------------------
FROM ${NODE_IMAGE} AS node_toolchain


# -----------------------------------------------------------------------------
# check
# -----------------------------------------------------------------------------
FROM ${PYTHON_IMAGE} AS check

COPY --from=node_toolchain /usr/local/bin/ /usr/local/bin/
COPY --from=node_toolchain /usr/local/lib/node_modules/ /usr/local/lib/node_modules/

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY int/ ./int/
RUN cd int && uv sync

COPY tester/package.json tester/package-lock.json ./tester/
RUN cd tester && npm ci

RUN ln -sfn /app/int/.venv/bin/ruff /usr/local/bin/ruff && \
    ln -sfn /app/int/.venv/bin/mypy /usr/local/bin/mypy && \
    ln -sfn /app/tester/node_modules/.bin/eslint /usr/local/bin/eslint && \
    ln -sfn /app/tester/node_modules/.bin/prettier /usr/local/bin/prettier && \
    ln -sfn /app/tester/node_modules/.bin/tsc /usr/local/bin/tsc

RUN mkdir -p /src && \
    ln -sfn /app/tester/node_modules /src/node_modules

WORKDIR /src
ENTRYPOINT ["bash"]


# -----------------------------------------------------------------------------
# build-test
# -----------------------------------------------------------------------------
FROM ${NODE_IMAGE} AS build-test

WORKDIR /app/tester

COPY tester/package.json tester/package-lock.json ./
RUN npm ci

COPY tester/ ./
RUN npm run build


# -----------------------------------------------------------------------------
# tester-runtime-deps
# -----------------------------------------------------------------------------
FROM ${NODE_IMAGE} AS tester-runtime-deps

WORKDIR /app/tester

COPY tester/package.json tester/package-lock.json ./
RUN npm ci --omit=dev


# -----------------------------------------------------------------------------
# runtime
# -----------------------------------------------------------------------------
FROM ${PYTHON_IMAGE} AS runtime

ENV VIRTUAL_ENV=/opt/runtime-python
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"
ENV PYTHONPATH="/app/int/src"

WORKDIR /app

COPY int/requirements.txt /tmp/int-requirements.txt
RUN python3 -m venv "${VIRTUAL_ENV}" && \
    "${VIRTUAL_ENV}/bin/pip" install --no-cache-dir -r /tmp/int-requirements.txt && \
    rm -f /tmp/int-requirements.txt

COPY int/src/ /app/int/src/

ENTRYPOINT ["python3", "/app/int/src/solint.py"]


# -----------------------------------------------------------------------------
# test
# -----------------------------------------------------------------------------
FROM runtime AS test

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    diffutils \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=node_toolchain /usr/local/bin/ /usr/local/bin/
COPY --from=node_toolchain /usr/local/lib/node_modules/ /usr/local/lib/node_modules/

WORKDIR /app/tester

COPY --from=tester-runtime-deps /app/tester/package.json ./package.json
COPY --from=tester-runtime-deps /app/tester/node_modules ./node_modules
COPY --from=build-test /app/tester/dist ./dist

COPY tester/tools/sol2xml ./tools/sol2xml

RUN pip install --no-cache-dir -r /app/tester/tools/sol2xml/requirements.txt

RUN chmod +x /app/int/src/solint.py && \
    ln -sfn /app/int/src/solint.py /usr/local/bin/solint

ENV SOL26_INTERPRETER=/usr/local/bin/solint
ENV SOL26_COMPILER_PYTHON=/opt/runtime-python/bin/python
ENV SOL26_COMPILER_SCRIPT=/app/tester/tools/sol2xml/sol_to_xml.py

ENTRYPOINT ["node", "/app/tester/dist/tester.js"]