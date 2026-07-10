"""
Module d'extraction de texte depuis des fichiers DOCX.
"""

from docx import Document


def extract_text_from_docx(file_path: str) -> str:
    """
    Extrait le texte brut d'un fichier .docx.

    Args:
        file_path: chemin vers le fichier .docx

    Returns:
        Le texte extrait, avec un paragraphe par ligne.
    """
    document = Document(file_path)

    paragraphs = [para.text for para in document.paragraphs if para.text.strip()]

    full_text = "\n".join(paragraphs)

    return full_text


if __name__ == "__main__":
    # Test rapide en exécutant directement ce fichier
    test_path = "data/raw/test_document.docx"
    result = extract_text_from_docx(test_path)
    print("--- Texte extrait ---")
    print(result)
    print(f"\n--- Longueur : {len(result)} caractères ---")