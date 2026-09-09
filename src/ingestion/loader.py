"""
Orchestrateur d'ingestion : detecte le type de fichier et appelle
l'extracteur approprie, avec bascule automatique vers l'OCR si un PDF
ne contient pas de texte natif exploitable.
"""

from pathlib import Path

from src.ingestion.docx_extractor import extract_text_from_docx
from src.ingestion.ocr_extractor import extract_text_from_pdf_ocr
from src.ingestion.pdf_extractor import extract_text_from_pdf

# Seuil en dessous duquel on considere que l'extraction native a echoue
# (PDF probablement scanne) et qu'il faut basculer sur l'OCR.
MIN_TEXT_LENGTH_THRESHOLD = 20
SUPPORTED_EXTENSIONS = {".docx", ".pdf", ".txt"}


def load_document(file_path: str) -> str:
    """
    Charge et extrait le texte d'un document supporte.

    Formats couverts :
    - DOCX
    - PDF natif
    - PDF scanne via OCR
    - TXT
    """
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".docx":
        return extract_text_from_docx(str(path))

    if extension == ".txt":
        return path.read_text(encoding="utf-8")

    if extension == ".pdf":
        native_text = extract_text_from_pdf(str(path))

        if len(native_text.strip()) >= MIN_TEXT_LENGTH_THRESHOLD:
            print(f"[INFO] {file_path} : extraction native reussie.")
            return native_text

        print(f"[INFO] {file_path} : texte natif insuffisant, bascule sur OCR.")
        return extract_text_from_pdf_ocr(str(path))

    raise ValueError(f"Format de fichier non supporte : {extension}")


def process_directory(input_dir: str = "data/raw", output_dir: str = "data/processed") -> None:
    """
    Traite tous les documents supportes d'un dossier et sauvegarde le texte
    extrait sous forme de fichiers .txt dans le dossier de sortie.
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    files = [f for f in input_path.iterdir() if f.suffix.lower() in SUPPORTED_EXTENSIONS]

    if not files:
        print(f"[WARNING] Aucun fichier supporte trouve dans {input_dir}")
        return

    for file in files:
        print(f"Traitement de : {file}")
        try:
            output_file = process_file(file, output_path)
        except Exception as exc:
            print(f"[ERROR] Echec du traitement de {file} : {exc}")
            continue

        print(f"  -> Sauvegarde dans {output_file}\n")


def process_file(file_path: str | Path, output_dir: str | Path = "data/processed") -> Path:
    """
    Traite un seul fichier source et retourne le chemin du texte extrait.
    """
    file = Path(file_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if file.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Format de fichier non supporte : {file.suffix.lower()}")

    text = load_document(str(file))
    safe_name = f"{file.stem}_{file.suffix.lstrip('.')}"
    output_file = output_path / f"{safe_name}.txt"
    output_file.write_text(text, encoding="utf-8")
    return output_file


if __name__ == "__main__":
    process_directory()
