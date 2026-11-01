# PDF Bewerbung Merger 📄🚀

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)

*English: An automated, cross-platform Python CLI tool to dynamically merge PDF job application documents (Cover Letter, CV, Certificates) into a single, ready-to-send file.*

---

## 📌 Über das Projekt (Motivation)
Wer viele Bewerbungen schreibt, kennt das Problem: Für jede Firma muss ein individuelles Anschreiben erstellt und anschließend manuell mit dem Lebenslauf sowie allen Zeugnissen und Zertifikaten in der richtigen Reihenfolge zu einer einzigen PDF-Datei zusammengefügt werden. Das kostet Zeit und ist fehleranfällig.

**PDF Bewerbung Merger** automatisiert diesen Prozess komplett. Ein einziger Befehl im Terminal reicht aus, um das passende Anschreiben zu greifen, alle Basisdokumente auf Vollständigkeit zu prüfen und die fertige Bewerbungsmappe sauber benannt im Ausgabeordner zu speichern.

## ✨ Features
* **Dynamische Zuordnung:** Findet automatisch das richtige Anschreiben anhand des übergebenen Firmennamens.
* **Strikte Reihenfolge:** Fügt alle Dokumente exakt in der in der `config.json` definierten Reihenfolge zusammen.
* **Integrierte Validierung:** Prüft vor dem Zusammenfügen, ob alle benötigten Dateien physisch vorhanden und gültige, unbeschädigte PDF-Dokumente sind.
* **100% Plattformübergreifend:** Funktioniert dank `pathlib` nahtlos unter Linux, macOS und Windows.
* **Vollautomatisches Setup:** Mitgelieferte Start-Skripte (`run.sh` und `run.bat`) richten automatisch eine isolierte virtuelle Umgebung (`.venv`) ein und installieren alle benötigten Abhängigkeiten im Hintergrund.
* **Out-of-the-Box Demo:** Enthält fertige Muster-Dokumente zum sofortigen Testen nach dem Klonen.

## 📁 Projektstruktur
```text
pdf-bewerbung-merger/
├── input/
│   ├── anschreiben/
│   │   └── Anschreiben Muster.pdf
│   └── base_docs/
│       ├── Lebenslauf Muster.pdf
│       ├── Arbeitszeugnis Muster.pdf
│       ├── Abschlusszeugnis Muster.pdf
│       └── Zertifikat Muster.pdf
├── output/                  # Hier landen die fertigen PDFs
├── config.json              # Zentrale Konfiguration für Pfade und Dateinamen
├── main.py                  # Hauptskript (Python)
├── requirements.txt         # Python-Abhängigkeiten (pypdf)
├── run.sh                   # Starter-Skript für Linux & macOS
└── run.bat                  # Starter-Skript für Windows
```

## ⚙️ Voraussetzungen
* **Python 3.x** muss auf dem System installiert sein.

## 🚀 Installation & Schnellstart (Mit Muster-Dateien)

1. **Repository klonen:**
   ```bash
   git clone [https://github.com/Denys-Yashyn/pdf-bewerbung-merger.git](https://github.com/Denys-Yashyn/pdf-bewerbung-merger.git)
   cd pdf-bewerbung-merger
   ```

2. **Testlauf mit den integrierten Muster-Dokumenten starten:**

   * **Linux & macOS:**
     ```bash
     chmod +x run.sh
     ./run.sh "Muster"
     ```
   * **Windows (CMD oder PowerShell):**
     ```cmd
     .\run.bat "Muster"
     ```

Das Skript erstellt automatisch die virtuelle Umgebung, installiert `pypdf`, fügt die Muster-Dokumente zusammen und speichert das Ergebnis unter `output/Bewerbung_<DeinSystemname>_Muster.pdf`.

*(Hinweis: Wenn der Firmenname Leerzeichen enthält, setze ihn einfach in Anführungszeichen, z. B. `./run.sh "Deutsche Bahn"`).*

## 🛠️ Eigene Dokumente einrichten (`config.json`)

Um das Tool für deine echten Bewerbungen zu nutzen:
1. Lege deine statischen Dokumente (Lebenslauf, Zeugnisse) im Ordner `input/base_docs/` ab.
2. Speichere deine individuellen Anschreiben im Ordner `input/anschreiben/` (z. B. `Anschreiben Telekom.pdf`).
3. Passe die Datei `config.json` an deine Dateinamen an:

```json
{
  "directories": {
    "input_dir": "input",
    "base_docs": "input/base_docs",
    "anschreiben": "input/anschreiben",
    "output": "output"
  },
  "templates": {
    "anschreiben": "Anschreiben {company}.pdf",
    "output_file": "Bewerbung {username} {company}.pdf"
  },
  "base_files": [
    "Lebenslauf.pdf",
    "Arbeitszeugnis.pdf",
    "Abschlusszeugnis.pdf",
    "Zertifikat.pdf"
  ]
}
```
* **Platzhalter `{company}`:** Wird durch das Argument ersetzt, das du im Terminal übergibst.
* **Platzhalter `{username}`:** Wird automatisch durch deinen aktuellen Systembenutzernamen ersetzt (kann in der `config.json` auch fest durch deinen echten Namen wie `"Max Mustermann"` überschrieben werden).
* * **Eigene Ordnerpfade (`directories`):** Du musst deine Dokumente nicht zwingend im Projektordner aufbewahren. In der `config.json` können problemlos auch **absolute Pfade** angegeben werden, um Dateien z. B. direkt aus deinem System-Dokumentenordner zu laden oder dort zu speichern:
  * **Linux / macOS:** `"/home/user/Documents/Bewerbungen/base_docs"`
  * **Windows:** `"C:/Users/Muster/Documents/Bewerbungen/base_docs"` *(Hinweis: Verwende in der JSON-Datei normale Schrägstriche `/` oder doppelte Backslashes `\\`)*.

## 📄 Lizenz
Dieses Projekt ist unter der **MIT-Lizenz** lizenziert – Details findest du in der Datei [LICENSE](LICENSE).
