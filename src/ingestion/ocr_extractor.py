"""
Module d'extraction de texte via OCR (Reconnaissance Optique de Caractères)
depuis des fichiers PDF scannés (contenant des images plutôt que du texte natif).
"""

from pdf2image import convert_from_path
import pytesseract


def extract_text_from_pdf_ocr(file_path: str, lang: str = "fra") -> str:
    """
    Extrait le texte d'un PDF scanné en convertissant chaque page en image
    puis en appliquant la reconnaissance optique de caractères (OCR).

    Args:
        file_path: chemin vers le fichier .pdf
        lang: langue utilisée par Tesseract pour la reconnaissance
              ("fra" pour français, "eng" pour anglais)

    Returns:
        Le texte reconnu par OCR, page après page.
    """
    images = convert_from_path(file_path)

    pages_text = []
    for image in images:
        text = pytesseract.image_to_string(image, lang=lang)
        if text:
            pages_text.append(text.strip())

    full_text = "\n".join(pages_text)

    return full_text


if __name__ == "__main__":
    test_path = "data/raw/test_document_scan.pdf"
    result = extract_text_from_pdf_ocr(test_path)
    print("--- Texte extrait via OCR ---")
    print(result)
    print(f"\n--- Longueur : {len(result)} caractères ---")