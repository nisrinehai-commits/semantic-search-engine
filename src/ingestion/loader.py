"""
Orchestrateur d'ingestion : détecte le type de fichier et appelle
l'extracteur approprié, avec bascule automatique vers l'OCR si un PDF
ne contient pas de texte natif exploitable.
"""

from pathlib import Path
from pydoc import text

from src.ingestion.docx_extractor import extract_text_from_docx
from src.ingestion.pdf_extractor import extract_text_from_pdf
from src.ingestion.ocr_extractor import extract_text_from_pdf_ocr

# Seuil en dessous duquel on considère que l'extraction native a échoué
# (PDF probablement scanné) et qu'il faut basculer sur l'OCR.
MIN_TEXT_LENGTH_THRESHOLD = 20


def load_document(file_path: str) -> str:
    """
    Charge et extrait le texte d'un document, quel que soit son format
    (.docx, .pdf natif, ou .pdf scanné).

    Args:
        file_path: chemin vers le fichier à traiter

    Returns:
        Le texte extrait du document.

    Raises:
        ValueError: si l'extension du fichier n'est pas supportée.
    """
    extension = Path(file_path).suffix.lower()

    if extension == ".docx":
        return extract_text_from_docx(file_path)

    elif extension == ".pdf":
        native_text = extract_text_from_pdf(file_path)

        if len(native_text.strip()) >= MIN_TEXT_LENGTH_THRESHOLD:
            print(f"[INFO] {file_path} : extraction native réussie.")
            return native_text
        else:
            print(f"[INFO] {file_path} : texte natif insuffisant, bascule sur OCR.")
            return extract_text_from_pdf_ocr(file_path)

    else:
        raise ValueError(f"Format de fichier non supporté : {extension}")


def process_directory(input_dir: str = "data/raw", output_dir: str = "data/processed") -> None:
    """
    Traite tous les documents supportés d'un dossier et sauvegarde
    le texte extrait sous forme de fichiers .txt dans le dossier de sortie.

    Args:
        input_dir: dossier contenant les documents source
        output_dir: dossier où sauvegarder les fichiers .txt extraits
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    supported_extensions = {".docx", ".pdf"}

    files = [f for f in input_path.iterdir() if f.suffix.lower() in supported_extensions]

    if not files:
        print(f"[WARNING] Aucun fichier supporté trouvé dans {input_dir}")
        return

    for file in files:
        print(f"Traitement de : {file}")
        try:
            text = load_document(str(file))
        except Exception as e:
            print(f"[ERROR] Échec du traitement de {file} : {e}")
            continue

        safe_name = f"{file.stem}_{file.suffix.lstrip('.')}"
        output_file = output_path / f"{safe_name}.txt"
        output_file.write_text(text, encoding="utf-8")
        print(f"  → Sauvegardé dans {output_file} ({len(text)} caractères)\n")


if __name__ == "__main__":
    process_directory()

    