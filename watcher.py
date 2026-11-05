import time
import subprocess
import sys
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def load_config(config_path="config.json"):
    """Lädt die Konfigurationsdatei."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Fehler: {config_path} nicht gefunden!")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Fehler: {config_path} ist fehlerhaft formatiert!")
        sys.exit(1)

class AnschreibenHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Реагируем только на создание новых файлов с расширением .pdf
        if not event.is_directory and event.src_path.lower().endswith('.pdf'):
            file_path = Path(event.src_path)
            print(f"\n📄 Neues Dokument erkannt: {file_path.name}")
            
            # Извлекаем имя компании
            company_name = file_path.stem.replace("Anschreiben", "").strip(" _-")
            
            if company_name:
                print(f"🚀 Starte Bewerbungs-Build für: {company_name}")
                try:
                    subprocess.run([sys.executable, "main.py", company_name], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"❌ Fehler beim Erstellen der PDF: {e}")
            else:
                print("⚠️ Firmenname konnte aus dem Dateinamen nicht ermittelt werden.")

if __name__ == "__main__":
    # 1. Читаем конфиг
    config = load_config()
    
    # 2. Достаем путь к папке Anschreiben (с фоллбэком на дефолтный путь)
    watch_directory = config.get("directories", {}).get("anschreiben", "input/anschreiben")
    
    # 3. Убедимся, что папка существует
    Path(watch_directory).mkdir(parents=True, exist_ok=True)
    
    event_handler = AnschreibenHandler()
    observer = Observer()
    
    # Настраиваем наблюдателя
    observer.schedule(event_handler, watch_directory, recursive=False)
    
    print(f"👀 Beobachte Ordner '{watch_directory}' aus config.json... (Abbruch mit Ctrl+C)")
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Beobachter beendet.")
        observer.stop()
    observer.join()
