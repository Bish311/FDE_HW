#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=== AI Procurement Request Copilot Startup ==="

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv || python -m venv .venv
    source .venv/bin/activate || source .venv/Scripts/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate || source .venv/Scripts/activate
fi

echo "Running pre-flight verification..."
python verify_setup.py

if [ -d "frontend" ] && [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend && npm install && cd ..
fi

echo "Starting services..."
python run_local.py
