#!/bin/bash
cd "$(dirname "$0")"

echo "🔄 Starte PDF Bewerbung Watcher..."

if [ ! -d ".venv" ]; then
    echo "❌ Fehler: Virtuelle Umgebung (.venv) fehlt!"
    echo "Bitte führe zuerst ./run.sh aus, um das Setup abzuschließen."
    exit 1
fi

exec .venv/bin/python watcher.py
