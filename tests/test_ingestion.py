"""
Tests unitaires pour le module d'ingestion de documents.
"""

from src.ingestion.loader import load_document
from src.ingestion.docx_extractor import extract_text_from_docx
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


def test_load_document_unsupported_format():
    try:
        load_document("data/raw/fichier_inexistant.txt")
        assert False, "Une ValueError aurait dû être levée"
    except ValueError:
        pass