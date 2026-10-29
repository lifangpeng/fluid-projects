#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
docker run --rm \
  --mount "type=bind,source=$project_dir,target=/input,readonly" \
  --workdir /tmp \
  python:3.12-slim \
  python /input/scripts/verify_skill_install.py
