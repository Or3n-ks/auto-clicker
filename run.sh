#!/usr/bin/env bash
# Launch the Kingshot autoclicker using the centralized venv.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec /Users/Oren.Brigg/Python/copilot/.venv/bin/python "$DIR/autoclicker.py" "$@"
