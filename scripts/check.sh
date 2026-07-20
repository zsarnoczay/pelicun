#!/bin/bash
#
# Local mirror of the CI checks. Run from the repository root:
#     ./scripts/check.sh
#
# Non-mutating: every step only reports problems; nothing rewrites files
#
set -e

# Sync the environment unless the caller (e.g. CI) already did so.
if [ "${UV_NO_SYNC:-0}" != "1" ]; then
    uv sync --extra test --extra lint
    export UV_NO_SYNC=1
fi

echo '=== Stage 1: Lint & Format ==='

echo 'Running Ruff Linter...'
uv run ruff check pelicun doc/source setup.py

echo 'Running Ruff Formatter Check...'
uv run ruff format --check pelicun doc/source setup.py

echo 'Running Codespell...'
uv run codespell pelicun doc/source README.md CHANGELOG.md

echo '=== Stage 2: Tests ==='

echo 'Running Pytest with Coverage...'
uv run python -m pytest pelicun/tests --cov=pelicun -n auto

echo 'All checks passed!'
