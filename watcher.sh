#!/bin/bash

echo "🔄 Starte PDF Bewerbung Watcher..."

# Проверяем, создано ли виртуальное окружение
if [ ! -d ".venv" ]; then
    echo "❌ Fehler: Virtuelle Umgebung (.venv) fehlt!"
    echo "Bitte führe zuerst ./run.sh aus, um das Setup abzuschließen."
    exit 1
fi

# Активируем окружение и запускаем скрипт
source .venv/bin/activate
python watcher.py
