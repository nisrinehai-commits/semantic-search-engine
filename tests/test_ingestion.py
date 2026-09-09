"""
Tests unitaires pour le module d'ingestion de documents.
"""

import pytest

from src.ingestion.docx_extractor import extract_text_from_docx
from src.ingestion.loader import load_document
from src.ingestion.pdf_extractor import extract_text_from_pdf


def test_extract_text_from_docx():
    text = extract_text_from_docx("data/raw/test_document.docx")
    assert len(text) > 0
    assert "INRH" in text


def test_extract_text_from_pdf_native():
    text = extract_text_from_pdf("data/raw/test_document.pdf")
    assert len(text) > 0
    assert "INRH" in text


def test_load_document_docx():
    text = load_document("data/raw/test_document.docx")
    assert len(text) > 0


def test_load_document_pdf_native():
    text = load_document("data/raw/test_document.pdf")
    assert len(text) > 0


def test_load_document_txt(tmp_path):
    file_path = tmp_path / "note.txt"
    file_path.write_text("Document texte simple pour la recherche semantique.", encoding="utf-8")

    assert "recherche semantique" in load_document(str(file_path))


def test_load_document_unsupported_format():
    with pytest.raises(ValueError):
        load_document("data/raw/fichier_inexistant.xlsx")
