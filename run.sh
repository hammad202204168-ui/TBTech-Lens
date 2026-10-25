#!/usr/bin/env bash
# Start TBTech Lens (web page + API) on http://localhost:8000   (API docs: /docs)
cd "$(dirname "$0")"
exec python -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
