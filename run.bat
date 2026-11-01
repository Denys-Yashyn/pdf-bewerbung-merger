@echo off
chcp 65001 >nul

if "%~1"=="" (
    echo [Fehler] Firmenname wurde nicht angegeben!
    echo [Info] Verwendung: run.bat "Firmenname"
    exit /b 1
)

set COMPANY_NAME=%~1

if not exist ".venv" (
    echo [Info] Virtuelle Umgebung .venv wird erstellt...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo [Info] Abhaengigkeiten aus requirements.txt werden installiert...
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q

echo [Info] PDF wird generiert...
python main.py "%COMPANY_NAME%"

call deactivate
