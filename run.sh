#!/usr/bin/env bash
cd "$(dirname "$0")"

# Use the active venv, or ./.venv or ./venv, or the system python3 as a last resort
if [ -n "$VIRTUAL_ENV" ]; then
    PY="$VIRTUAL_ENV/bin/python"
elif [ -x .venv/bin/python ]; then
    PY=.venv/bin/python
elif [ -x venv/bin/python ]; then
    PY=venv/bin/python
else
    PY=python3
fi

# web.py also starts the Slack bot in the background
exec $PY -m uvicorn web:app --host "${IP:-0.0.0.0}" --port "${PORT:-8000}"
