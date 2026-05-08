#!/bin/bash
set -e

echo "--- Running Ruff (Linting) ---"
ruff check .

echo "--- Running MyPy (Type Safety) ---"
mypy .

echo "--- Running Pytest (Unit & E2E) ---"
pytest tests/
