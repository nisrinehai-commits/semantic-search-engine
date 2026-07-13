"""
Tests unitaires pour l'API REST.
"""

from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_endpoint_returns_results():
    response = client.post("/search", json={
        "query": "recherche sur les ressources de pêche",
        "top_k": 3
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 3


def test_search_endpoint_default_top_k():
    response = client.post("/search", json={
        "query": "recherche sur les ressources de pêche"
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 3  # top_k par défaut = 3


def test_search_endpoint_rejects_empty_query():
    response = client.post("/search", json={"query": "", "top_k": 3})
    assert response.status_code == 422  # erreur de validation Pydantic


def test_search_endpoint_rejects_invalid_top_k():
    response = client.post("/search", json={"query": "test", "top_k": 100})
    assert response.status_code == 422  # top_k > 20, hors limite définie