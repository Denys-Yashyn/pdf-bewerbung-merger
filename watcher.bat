@echo off
echo 🔄 Starte PDF Bewerbung Watcher...

IF NOT EXIST ".venv" (
    echo ❌ Fehler: Virtuelle Umgebung (.venv) fehlt!
    echo Bitte fuehre zuerst run.bat aus, um das Setup abzuscliessen.
    pause
    exit /b 1
)

call .venv\Scripts\activate
python watcher.py
pause
