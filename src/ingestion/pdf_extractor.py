"""
Module d'extraction de texte natif depuis des fichiers PDF
(fonctionne uniquement si le PDF contient du texte réel, pas des images scannées).
"""

from pypdf import PdfReader


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extrait le texte natif d'un fichier PDF (texte réellement présent,
    pas via OCR).

    Args:
        file_path: chemin vers le fichier .pdf

    Returns:
        Le texte extrait, une page après l'autre. Chaîne vide si le PDF
        ne contient pas de texte natif (probablement un PDF scanné).
    """
    reader = PdfReader(file_path)

    pages_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text)

    full_text = "\n".join(pages_text)

    return full_text


if __name__ == "__main__":
    # Test sur le PDF avec texte natif
    test_path = "data/raw/test_document.pdf"
    result = extract_text_from_pdf(test_path)
    print("--- Texte extrait (PDF natif) ---")
    print(result)
    print(f"\n--- Longueur : {len(result)} caractères ---")

    # Test sur le PDF scanné (doit donner un résultat vide ou quasi vide)
    print("\n" + "=" * 50)
    test_path_scan = "data/raw/test_document_scan.pdf"
    result_scan = extract_text_from_pdf(test_path_scan)
    print("--- Texte extrait (PDF scanné, doit être vide) ---")
    print(repr(result_scan))
    print(f"\n--- Longueur : {len(result_scan)} caractères ---")