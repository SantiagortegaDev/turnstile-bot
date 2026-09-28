#!/usr/bin/env bash
cd "$(dirname "$0")"

PY=.venv/bin/python

$PY bot.py &
BOT_PID=$!

$PY -m uvicorn web:app --host 0.0.0.0 --port 8000 &
WEB_PID=$!

trap "kill $BOT_PID $WEB_PID 2>/dev/null" EXIT INT TERM
wait
