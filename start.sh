#!/bin/sh
set -e
uvicorn app.main:app --host 0.0.0.0 --port 8081 &
exec streamlit run frontend/streamlit_app.py --server.address 0.0.0.0 --server.port "${PORT:-8080}" --server.headless true --server.enableCORS false
