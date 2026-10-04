#!/usr/bin/env bash
cd "$(dirname "$0")"

if [ -n "$VIRTUAL_ENV" ]; then
    PY="$VIRTUAL_ENV/bin/python"
elif [ -x .venv/bin/python ]; then
    PY=.venv/bin/python
elif [ -x venv/bin/python ]; then
    PY=venv/bin/python
else
    PY=python3
fi

exec $PY -m uvicorn web:app --host "${IP:-0.0.0.0}" --port "${PORT:-8000}"
