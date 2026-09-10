"""
Tests unitaires pour le moteur de recherche semantique.
"""

from src.search.search_engine import search


def test_search_returns_results():
    results = search("recherche sur les ressources de peche", top_k=3)
    assert len(results) == 3


def test_search_results_are_sorted_by_score():
    results = search("recherche sur les ressources de peche", top_k=3)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_search_returns_chunk_metadata():
    results = search("recherche sur les ressources de peche", top_k=1)
    result = results[0]

    assert "filename" in result
    assert "source_type" in result
    assert "chunk_id" in result
    assert "start_char" in result
    assert "end_char" in result
    assert result["end_char"] >= result["start_char"]
    assert "semantic_score" in result
    assert "keyword_score" in result
    assert "search_mode" in result


def test_search_top_k_respects_limit():
    results = search("test", top_k=2)
    assert len(results) == 2


def test_search_keyword_mode_returns_results():
    results = search("aquaculture", top_k=2, mode="keyword")
    assert len(results) == 2
    assert all(result["search_mode"] == "keyword" for result in results)


def test_search_hybrid_mode_returns_final_scores():
    results = search("peche durable", top_k=3, mode="hybrid", semantic_weight=0.7, keyword_weight=0.3)
    assert len(results) == 3
    assert all(0 <= result["score"] <= 1 for result in results)


def test_search_prefers_fishing_document_for_fishing_query():
    results = search("rapport peche", top_k=5, mode="hybrid")
    assert results[0]["filename"] == "doc_peche_durable_docx.txt"
