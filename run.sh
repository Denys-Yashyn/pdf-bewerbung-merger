#!/bin/bash
set -e
cd "$(dirname "$0")"

# Prüfen, ob der Firmenname als Argument übergeben wurde
if [ -z "$1" ]; then
    echo "❌ Fehler: Firmenname wurde nicht angegeben!"
    echo "💡 Verwendung: ./run.sh \"Firmenname\" [-p Position] [-c Ort] [-n Notiz]"
    exit 1
fi

# Virtuelle Umgebung erstellen, falls nicht vorhanden
if [ ! -d ".venv" ]; then
    echo "⚙️ Virtuelle Umgebung (.venv) wird erstellt..."
    python3 -m venv .venv
fi

# Abhängigkeiten nur installieren, wenn sich requirements.txt geändert hat
if [ requirements.txt -nt .venv/.deps-installed ]; then
    echo "📦 Abhängigkeiten aus requirements.txt werden installiert..."
    .venv/bin/pip install -q -r requirements.txt
    touch .venv/.deps-installed
fi

echo "🚀 PDF wird generiert..."
.venv/bin/python main.py "$@"
