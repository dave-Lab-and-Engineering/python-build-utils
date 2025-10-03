#!/usr/bin/env bash
set -euo pipefail

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install binary to /usr/local/bin
if [ -x "$HOME/.local/bin/uv" ]; then
  sudo install -m 0755 "$HOME/.local/bin/uv" /usr/local/bin/uv
elif [ -x "$HOME/.cargo/bin/uv" ]; then
  sudo install -m 0755 "$HOME/.cargo/bin/uv" /usr/local/bin/uv
fi

uv --version

uv sync
uv run pre-commit install --install-hooks --overwrite
