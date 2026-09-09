"""
Decoupage des documents en passages courts pour ameliorer la precision
de la recherche semantique et preparer un futur module RAG.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    """Passage textuel indexable."""

    chunk_id: int
    text: str
    start_char: int
    end_char: int


def normalize_text(text: str) -> str:
    """Nettoie les espaces sans detruire les sauts de paragraphe utiles."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_into_chunks(text: str, max_chars: int = 900, overlap: int = 180) -> list[TextChunk]:
    """
    Decoupe un texte en passages chevauchants.

    Le chevauchement evite de perdre une information placee a la frontiere
    entre deux passages.
    """
    cleaned = normalize_text(text)
    if not cleaned:
        return []

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", cleaned) if p.strip()]
    chunks: list[TextChunk] = []
    buffer = ""
    buffer_start = 0
    cursor = 0

    for paragraph in paragraphs:
        paragraph_start = cleaned.find(paragraph, cursor)
        if paragraph_start == -1:
            paragraph_start = cursor
        cursor = paragraph_start + len(paragraph)

        candidate = f"{buffer}\n\n{paragraph}".strip() if buffer else paragraph
        if buffer and len(candidate) > max_chars:
            chunks.append(_make_chunk(len(chunks), buffer, buffer_start))
            tail = buffer[-overlap:].strip() if overlap > 0 else ""
            buffer = f"{tail}\n\n{paragraph}".strip() if tail else paragraph
            buffer_start = max(0, paragraph_start - len(tail))
        else:
            if not buffer:
                buffer_start = paragraph_start
            buffer = candidate

        while len(buffer) > max_chars:
            split_at = _find_split_position(buffer, max_chars)
            chunk_text = buffer[:split_at].strip()
            chunks.append(_make_chunk(len(chunks), chunk_text, buffer_start))
            tail_start = max(0, split_at - overlap)
            buffer = buffer[tail_start:].strip()
            buffer_start += tail_start

    if buffer:
        chunks.append(_make_chunk(len(chunks), buffer, buffer_start))

    return chunks


def _find_split_position(text: str, max_chars: int) -> int:
    window = text[:max_chars]
    for separator in (". ", "\n", "; ", ", "):
        pos = window.rfind(separator)
        if pos >= max_chars * 0.55:
            return pos + len(separator)
    return max_chars


def _make_chunk(chunk_id: int, text: str, start_char: int) -> TextChunk:
    text = text.strip()
    return TextChunk(
        chunk_id=chunk_id,
        text=text,
        start_char=start_char,
        end_char=start_char + len(text),
    )
