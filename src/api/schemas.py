"""
Schémas de données (requêtes/réponses) pour l'API de recherche sémantique.
"""

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Corps de la requête POST /search."""
    query: str = Field(..., min_length=1, description="Texte de la requête utilisateur")
    top_k: int = Field(default=3, ge=1, le=20, description="Nombre de résultats à retourner")


class SearchResult(BaseModel):
    """Un résultat individuel de recherche."""
    filename: str
    score: float
    text_preview: str


class SearchResponse(BaseModel):
    """Corps de la réponse de POST /search."""
    query: str
    results: list[SearchResult]