"""
API REST du moteur de recherche sémantique.
"""

from fastapi import FastAPI, HTTPException

from src.api.schemas import SearchRequest, SearchResponse, SearchResult
from src.search.search_engine import search

app = FastAPI(
    title="Moteur de Recherche Sémantique — INRH",
    description="API de recherche sémantique basée sur SBERT et FAISS.",
    version="1.0.0",
)


@app.get("/")
def root():
    """Message de bienvenue / vérification que l'API tourne."""
    return {"message": "Moteur de recherche sémantique INRH — API opérationnelle."}


@app.get("/health")
def health():
    """Endpoint de santé, utile pour du monitoring futur."""
    return {"status": "ok"}


@app.post("/search", response_model=SearchResponse)
def search_documents(request: SearchRequest):
    """
    Recherche les documents les plus pertinents pour une requête donnée.
    """
    try:
        raw_results = search(request.query, top_k=request.top_k)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    results = [SearchResult(**r) for r in raw_results]

    return SearchResponse(query=request.query, results=results)