import re
import subprocess
import sys
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from main import fill_template, load_config

SCRIPT_DIR = Path(__file__).resolve().parent


def build_filename_pattern(template: str) -> re.Pattern:
    """Turn the Anschreiben filename template from config.json into a regex.

    With a template like "Anschreiben_{company}_{city}.pdf" the company may contain
    underscores, the city may not: Anschreiben_Foo_Bar_Ulm.pdf -> "Foo_Bar", "Ulm".
    """
    pattern = re.escape(fill_template(template, "{company}", "{city}"))
    pattern = pattern.replace(r"\{company\}", r"(?P<company>.+)")
    pattern = pattern.replace(r"\{city\}", r"(?P<city>[^_]+)")
    return re.compile(pattern, re.IGNORECASE)


def wait_until_written(path: Path, timeout: float = 30.0) -> bool:
    """Wait until the file size stops changing, i.e. the writer has finished saving."""
    deadline = time.monotonic() + timeout
    last_size = -1
    while time.monotonic() < deadline:
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            return False
        if size > 0 and size == last_size:
            return True
        last_size = size
        time.sleep(0.5)
    return False


class AnschreibenHandler(FileSystemEventHandler):
    def __init__(self, pattern: re.Pattern):
        self.pattern = pattern

    def on_created(self, event):
        self._handle(event.is_directory, event.src_path)

    def on_moved(self, event):
        # Many programs save to a temp file and rename it afterwards
        self._handle(event.is_directory, event.dest_path)

    def _handle(self, is_directory: bool, path: str) -> None:
        file_path = Path(path)
        if is_directory or file_path.suffix.lower() != ".pdf":
            return

        print(f"\n📄 Neues Dokument erkannt: {file_path.name}")
        match = self.pattern.fullmatch(file_path.name)
        if not match:
            print("⚠️ Dateiname entspricht nicht der Vorlage 'templates.anschreiben' aus config.json.")
            return
        if not wait_until_written(file_path):
            print("⚠️ Datei wurde nicht vollständig geschrieben, übersprungen.")
            return

        command = [sys.executable, str(SCRIPT_DIR / "main.py"), match["company"]]
        city = match.groupdict().get("city")
        if city:
            command += ["-c", city]

        print(f"🚀 Starte Bewerbungs-Build für: {match['company']}")
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Fehler beim Erstellen der PDF: {e}")


if __name__ == "__main__":
    config = load_config(SCRIPT_DIR / "config.json")
    watch_directory = (SCRIPT_DIR / config["directories"]["anschreiben"]).resolve()
    watch_directory.mkdir(parents=True, exist_ok=True)

    observer = Observer()
    observer.schedule(
        AnschreibenHandler(build_filename_pattern(config["templates"]["anschreiben"])),
        str(watch_directory),
        recursive=False,
    )

    print(f"👀 Beobachte Ordner '{watch_directory}' aus config.json... (Abbruch mit Ctrl+C)")
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Beobachter beendet.")
        observer.stop()
    observer.join()
