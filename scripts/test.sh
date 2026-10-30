#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python -m compileall -q backend manage.py
PYTHONPATH=. pytest -q tests/test_portal.py
if command -v node >/dev/null 2>&1; then node --check web/assets/portal.js; fi
