@echo off
echo 🔄 Starte PDF Bewerbung Watcher...

IF NOT EXIST ".venv" (
    echo ⚠️ Virtuelle Umgebung .venv fehlt. Starte automatisches Setup...
    call run.bat "Setup"
    
    IF NOT EXIST ".venv" (
        echo ❌ Fehler: Automatisches Setup fehlgeschlagen.
        pause
        exit /b 1
    )
    echo ✅ Setup erfolgreich abgeschlossen!
)

call .venv\Scripts\activate
python watcher.py
pause
