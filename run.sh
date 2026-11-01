#!/bin/bash

# Prüfen, ob der Firmenname als Argument übergeben wurde
if [ -z "$1" ]; then
    echo "❌ Fehler: Firmenname wurde nicht angegeben!"
    echo "💡 Verwendung: ./run.sh \"Firmenname\""
    exit 1
fi

COMPANY_NAME="$1"

# Virtuelle Umgebung erstellen, falls nicht vorhanden
if [ ! -d ".venv" ]; then
    echo "⚙️ Virtuelle Umgebung (.venv) wird erstellt..."
    python3 -m venv .venv
fi

# Virtuelle Umgebung aktivieren
source .venv/bin/activate

# Abhängigkeiten installieren (im stillen Modus)
echo "📦 Abhängigkeiten aus requirements.txt werden installiert..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Das Python-Skript ausführen
echo "🚀 PDF wird generiert..."
python3 main.py "$COMPANY_NAME"

# Virtuelle Umgebung deaktivieren
deactivate