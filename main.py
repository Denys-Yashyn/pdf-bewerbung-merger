import argparse, json, sys, getpass, re
from pathlib import Path
from pypdf.errors import PdfReadError
from pypdf import PdfReader, PdfWriter

def load_config(config_path: Path) -> dict:
    # Lädt die Konfigurationsdatei
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Kritischer Fehler: Konfigurationsdatei wurde nicht gefunden unter:\n{config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Syntaxfehler in config.json: {e}")
        sys.exit(1)

def parse_arguments() -> str:
    # Verarbeitet die Befehlszeilenargumente
    parser = argparse.ArgumentParser(
        description="Ein Tool zum automatischen Zusammenfügen von PDF-Bewerbungsunterlagen."
    )
    
    parser.add_argument(
        "company",
        type=str,
        help="Name des Unternehmens (wird für das Anschreiben und den Dateinamen verwendet, z.B. Telekom)"
    )
    
    args = parser.parse_args()
    return args.company

def prepare_and_validate_files(company_name: str, config: dict, script_dir: Path) -> list[Path]:
    # Überprüft, ob alle benötigten PDF-Dateien existieren und gültig sind
    anschreiben_dir = (script_dir / config["directories"]["anschreiben"]).resolve()
    base_docs_dir = (script_dir / config["directories"]["base_docs"]).resolve()
    
    anschreiben_filename = config["templates"]["anschreiben"].format(company=company_name)
    anschreiben_path = anschreiben_dir / anschreiben_filename
    
    file_paths = [anschreiben_path]
    for base_file in config["base_files"]:
        file_paths.append(base_docs_dir / base_file)
        
    valid_paths = []
    
    for file_path in file_paths:
        if not file_path.exists():
            raise FileNotFoundError(f"Erforderliche Datei fehlt: {file_path}")
            
        if file_path.suffix.lower() != ".pdf":
            raise ValueError(f"PDF-Datei erwartet, aber folgendes erhalten: {file_path}")
            
        try:
            PdfReader(file_path)
        except PdfReadError:
            raise ValueError(f"Datei ist beschädigt oder keine gültige PDF: {file_path}")
            
        valid_paths.append(file_path)
        
    return valid_paths

def merge_pdfs(input_files: list[Path], output_path: Path) -> None:
    # Fügt die validierten PDF-Dateien zusammen und speichert das Ergebnis
    writer = PdfWriter()
    
    for file_path in input_files:
        writer.append(file_path)
        
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    writer.write(output_path)
    writer.close()

if __name__ == "__main__":
    company_name = parse_arguments()
    
    script_dir = Path(__file__).parent.resolve()
    config_path = script_dir / "config.json"
    config = load_config(config_path)
    
    print(f"Bewerbung für das Unternehmen {company_name} wird erstellt...")
    
    try:
        valid_files = prepare_and_validate_files(company_name, config, script_dir)
        
        # Systembenutzernamen abrufen (z.B. "MaxMustermann")
        system_user = getpass.getuser()
        # Entfernt ungültige Zeichen aus dem Benutzernamen für die Dateibenennung
        safe_username = re.sub(r'[\\/*?:"<>|]', "", system_user)
        
        output_dir = (script_dir / config["directories"]["output"]).resolve()
        
        # Formatierung mit Benutzer- und Firmennamen
        output_filename = config["templates"]["output_file"].format(
            username=safe_username,
            company=company_name
        )
        final_output_path = output_dir / output_filename
        
        merge_pdfs(valid_files, final_output_path)
        
        print(f"✅ Erfolg! Datei gespeichert unter: {final_output_path}")
        
    except Exception as e:
        print(f"❌ Vorgang aufgrund eines Fehlers abgebrochen:\n{e}")
        sys.exit(1)