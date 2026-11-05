import argparse, json, sys
from pathlib import Path
from pypdf.errors import PdfReadError
from pypdf import PdfReader, PdfWriter
from database import save_application_to_db

def load_config(config_path: Path) -> dict:
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config
    except FileNotFoundError:
        print(f"Config file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Invalid JSON in config file: {config_path}")
        sys.exit(1)
    

# return name of company
def parse_arguments() -> tuple[str, str]:
    parser = argparse.ArgumentParser(description="Tool zum Zusammenfügen von PDFs.")
    parser.add_argument("company", type=str, help="Name des Unternehmens")
    
    # optionsl argument 
    parser.add_argument(
        "-p", "--position", 
        type=str, 
        default="Fachinformatiker für Systemintegration", # Default value
        help="Position, auf die du dich bewirbst (z.B. 'Fachinformatiker für Systemintegration')"
    )
    
    args = parser.parse_args()
    return args.company, args.position

# Check if the files exist and are valid PDFs, return a list of valid file paths
# if any file is invalid, raise an exception
def prepare_and_validate_files(company_name: str, config: dict, script_dir: Path) -> list[Path]:
    # 1. Create Path objects for the directories specified in the config
    anschreiben_dir = (script_dir / config["directories"]["anschreiben"]).resolve()
    base_docs_dir = (script_dir / config["directories"]["base_docs"]).resolve()
    
    # 2. Substitute the company name in the template for Anschreiben
    anschreiben_filename = config["templates"]["anschreiben"].format(company=company_name)
    anschreiben_path = anschreiben_dir / anschreiben_filename
    
    # 3. Compile the final list of file paths (Anschreiben comes first, followed by base files)
    file_paths = [anschreiben_path]
    for base_file in config["base_files"]:
        file_paths.append(base_docs_dir / base_file)
        
    valid_paths = []
    
    # 4. Validate each file in the list
    for file_path in file_paths:
        # Check 1: Does the file exist physically?
        if not file_path.exists():
            raise FileNotFoundError(f"Required file is missing: {file_path}")
            
        # Check 2: Is the file extension correct?
        if file_path.suffix.lower() != ".pdf":
            raise ValueError(f"Expected a PDF file, but got: {file_path}")
            
        # Check 3: Is the file a valid PDF?
        try:
            PdfReader(file_path)
        except PdfReadError:
            raise ValueError(f"File is corrupted or not a valid PDF document: {file_path}")
            
        # if all checks pass, add the file path to the list of valid paths
        valid_paths.append(file_path)
        
    return valid_paths
    
# take a list of valid PDF file paths and use pypdf.PdfWriter to merge them into a single PDF file at the specified $output_path
def merge_pdfs(input_files: list[Path], output_path: Path) -> None:
    writer = PdfWriter()
    
    
    for file_path in input_files:
        writer.append(file_path)
        
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    
    writer.write(output_path)
    writer.close()

# parse_arguments -> load_config -> prepare_and_validate_files -> merge_pdfs -> print success message
def main():
    if __name__ == "__main__":   
    # 1. Get the company name and position title from command line arguments
        company_name, position_title = parse_arguments()
    
    # 2. Load the configuration from config.json
        script_dir = Path(__file__).parent.resolve()
        config_path = script_dir / "config.json"
        config = load_config(config_path)
    
        print(f"Forming application for company: {company_name}, position: {position_title}")
    
        try:
        # 3. Prepare and validate the input files
            valid_files = prepare_and_validate_files(company_name, config, script_dir)
        
        # 4. Form the path for saving the final file    
            output_dir = (script_dir / config["directories"]["output"]).resolve()
            output_filename = config["templates"]["output_file"].format(company=company_name)
            final_output_path = output_dir / output_filename
        
        # 5. Merge the valid PDF files into a single output file
            merge_pdfs(valid_files, final_output_path)
        
            print(f"✅ Success! File saved: {final_output_path}")
        
        # 6. Save the application details to the database  
            if config.get("use_database", False):
                from database import save_application_to_db
                save_application_to_db(company_name, position_title, final_output_path.resolve())
            else:
                print("ℹ️ Datenbank-Tracking ist in config.json deaktiviert. Überspringe Speicherung.")
        
        except Exception as e:
            print(f"❌ Process failed due to an error:\n{e}")
            sys.exit(1)

main()
