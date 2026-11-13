import argparse
import getpass
import json
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError


def load_config(config_path: Path) -> dict:
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Invalid JSON in config file: {config_path}")
        sys.exit(1)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tool zum Zusammenfügen von PDFs.")
    parser.add_argument("company", help="Name des Unternehmens (bei Leerzeichen in Anführungszeichen)")
    parser.add_argument(
        "-p", "--position",
        default="Fachinformatiker für Systemintegration",
        help="Position, auf die du dich bewirbst",
    )
    parser.add_argument("-c", "--city", default="", help="Ort des Unternehmens")
    parser.add_argument("-n", "--notes", default="", help="Notiz, z. B. Link zur Stellenanzeige")
    return parser.parse_args()


def fill_template(template: str, company: str, city: str) -> str:
    """Replace the {company}, {city} and {username} placeholders of a filename template."""
    return template.format(company=company, city=city, username=getpass.getuser())


def prepare_and_validate_files(company: str, city: str, config: dict, script_dir: Path) -> list[Path]:
    """Return the files to merge (Anschreiben first, then the base files); raise if one is missing or invalid."""
    anschreiben_dir = (script_dir / config["directories"]["anschreiben"]).resolve()
    base_docs_dir = (script_dir / config["directories"]["base_docs"]).resolve()

    file_paths = [anschreiben_dir / fill_template(config["templates"]["anschreiben"], company, city)]
    file_paths += [base_docs_dir / base_file for base_file in config["base_files"]]

    for file_path in file_paths:
        if not file_path.exists():
            raise FileNotFoundError(f"Required file is missing: {file_path}")
        if file_path.suffix.lower() != ".pdf":
            raise ValueError(f"Expected a PDF file, but got: {file_path}")
        try:
            PdfReader(file_path)
        except PdfReadError:
            raise ValueError(f"File is corrupted or not a valid PDF document: {file_path}")
    return file_paths


def merge_pdfs(input_files: list[Path], output_path: Path) -> None:
    writer = PdfWriter()
    for file_path in input_files:
        writer.append(file_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer.write(output_path)
    writer.close()


def main() -> None:
    args = parse_arguments()
    script_dir = Path(__file__).resolve().parent
    config = load_config(script_dir / "config.json")
    print(f"Forming application for company: {args.company}, position: {args.position}")

    try:
        valid_files = prepare_and_validate_files(args.company, args.city, config, script_dir)
        output_dir = (script_dir / config["directories"]["output"]).resolve()
        output_path = output_dir / fill_template(config["templates"]["output_file"], args.company, args.city)

        merge_pdfs(valid_files, output_path)
        print(f"✅ Success! File saved: {output_path}")

        if config.get("use_database", False):
            from database import save_application_to_db  # DB dependencies are only needed when tracking is on
            save_application_to_db(args.company, args.position, output_path, args.city, args.notes)
        else:
            print("ℹ️ Datenbank-Tracking ist in config.json deaktiviert. Überspringe Speicherung.")
    except Exception as e:
        print(f"❌ Process failed due to an error:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
