#!/usr/bin/env bash
# Create .venv and install dependencies (avoids PEP 668 "externally-managed-environment" on Homebrew Python).
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt

echo ""
echo "Setup complete. Run the app with:"
echo "  source .venv/bin/activate"
echo "  python main.py"
echo ""
echo "Or without activating:"
echo "  ./.venv/bin/python main.py"
