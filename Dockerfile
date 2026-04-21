FROM node:24.12-bookworm-slim AS node_toolchain


FROM python:3.14-slim AS check

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY --from=node_toolchain /usr/local/bin/ /usr/local/bin/
COPY --from=node_toolchain /usr/local/lib/node_modules/ /usr/local/lib/node_modules/

WORKDIR /app

COPY int/ ./int/
RUN cd int && uv sync

COPY tester/package.json tester/package-lock.json ./tester/
RUN cd tester && npm ci

RUN mkdir -p /usr/local/lib/ipp /src/int /src/tester && \
    cat > /usr/local/lib/ipp/check-shell-init.sh <<'BASH'
#!/bin/bash
set -euo pipefail

mkdir -p /src/int /src/tester

ln -sfn /app/int/.venv/bin/ruff /src/int/ruff
ln -sfn /app/int/.venv/bin/mypy /src/int/mypy
ln -sfn /app/tester/node_modules/.bin/eslint /src/tester/eslint
ln -sfn /app/tester/node_modules/.bin/prettier /src/tester/prettier
BASH

RUN chmod +x /usr/local/lib/ipp/check-shell-init.sh

WORKDIR /src
ENV BASH_ENV=/usr/local/lib/ipp/check-shell-init.sh
ENTRYPOINT ["/bin/bash"]


FROM node:24.12-bookworm-slim AS build-test

WORKDIR /app/tester

COPY tester/package.json tester/package-lock.json ./
RUN npm install

COPY tester/ ./
RUN npm run build


FROM python:3.14-slim AS runtime

WORKDIR /app

COPY int/requirements.txt ./requirements.txt
RUN python3 -m venv /opt/runtime-python && \
    /opt/runtime-python/bin/pip install --no-cache-dir -r /app/requirements.txt

COPY int/src ./int/src

ENV PATH="/opt/runtime-python/bin:${PATH}"
ENV PYTHONPATH="/app/int/src"

ENTRYPOINT ["/opt/runtime-python/bin/python", "/app/int/src/solint.py"]


FROM runtime AS test

RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    npm \
    gcc \
    libxml2-dev \
    libxslt-dev \
    zlib1g-dev \
    diffutils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/tester

COPY tester/package.json tester/package-lock.json ./
RUN npm install --omit=dev

COPY --from=build-test /app/tester/dist ./dist
COPY tester/tools/sol2xml ./tools/sol2xml

RUN pip install --no-cache-dir -r /app/tester/tools/sol2xml/requirements.txt
RUN chmod +x /app/int/src/solint.py && \
    ln -sfn /app/int/src/solint.py /usr/local/bin/solint

ENTRYPOINT ["node", "/app/tester/dist/tester.js"]