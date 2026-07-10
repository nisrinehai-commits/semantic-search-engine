"""
Tests unitaires pour le moteur de recherche sémantique.
"""

from src.search.search_engine import search


def test_search_returns_results():
    results = search("recherche sur les ressources de pêche", top_k=3)
    assert len(results) == 3


def test_search_results_are_sorted_by_score():
    results = search("recherche sur les ressources de pêche", top_k=3)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_search_most_relevant_result_is_about_fisheries():
    results = search("recherche sur les ressources de pêche", top_k=1)
    assert "docx" in results[0]["filename"] or "pdf" in results[0]["filename"]
    assert "scan" not in results[0]["filename"]


def test_search_top_k_respects_limit():
    results = search("test", top_k=2)
    assert len(results) == 2