"""
Moteur de recherche documentaire.

Modes supportes :
- semantic : similarite vectorielle FAISS / embeddings ;
- keyword : score lexical BM25 simplifie ;
- hybrid : fusion ponderee semantic + keyword.
"""

import json
import math
import re
from pathlib import Path

import numpy as np

EMBEDDINGS_DIR = "data/embeddings"


def load_index(embeddings_dir: str = EMBEDDINGS_DIR):
    """Charge l'index FAISS et les metadonnees associees."""
    index_path = Path(embeddings_dir) / "faiss_index.bin"
    metadata_path = Path(embeddings_dir) / "metadata.json"

    if not index_path.exists() or not metadata_path.exists():
        raise FileNotFoundError(
            "Index introuvable. Lance d'abord : python -m src.embeddings.build_index"
        )

    import faiss

    index = faiss.read_index(str(index_path))
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    return index, metadata


def search(
    query: str,
    top_k: int = 3,
    embeddings_dir: str = EMBEDDINGS_DIR,
    mode: str = "hybrid",
    semantic_weight: float = 0.7,
    keyword_weight: float = 0.3,
):
    """
    Recherche les passages les plus pertinents.

    En mode hybride, le score final est :
    semantic_weight * score_semantique + keyword_weight * score_mots_cles
    """
    index, metadata = load_index(embeddings_dir)
    mode = normalize_mode(mode)
    semantic_weight, keyword_weight = normalize_weights(semantic_weight, keyword_weight, mode)

    safe_top_k = min(top_k, len(metadata))
    semantic_scores = semantic_search_scores(query, index, metadata)
    keyword_scores = bm25_scores(query, metadata)

    if mode == "semantic":
        final_scores = semantic_scores
    elif mode == "keyword":
        final_scores = keyword_scores
    else:
        final_scores = (semantic_weight * semantic_scores) + (keyword_weight * keyword_scores)

    ranked_indices = np.argsort(final_scores)[::-1][:safe_top_k]

    results = []
    for idx in ranked_indices:
        if idx == -1:
            continue

        item = metadata[idx]
        results.append(
            {
                "filename": item["filename"],
                "source_type": item.get("source_type", "unknown"),
                "chunk_id": item.get("chunk_id", 0),
                "start_char": item.get("start_char", 0),
                "end_char": item.get("end_char", 0),
                "score": float(final_scores[idx]),
                "semantic_score": float(semantic_scores[idx]),
                "keyword_score": float(keyword_scores[idx]),
                "search_mode": mode,
                "text_preview": item["text_preview"],
            }
        )

    return results


def semantic_search_scores(query: str, index, metadata: list[dict]) -> np.ndarray:
    """Calcule un score semantique normalise pour chaque passage."""
    try:
        import faiss

        from src.embeddings.embedder import generate_embedding

        query_vector = generate_embedding(query).astype("float32").reshape(1, -1)
        faiss.normalize_L2(query_vector)
        scores, indices = index.search(query_vector, len(metadata))
    except RuntimeError:
        return tfidf_scores(query, metadata)

    semantic_scores = np.zeros(len(metadata), dtype="float32")
    for score, idx in zip(scores[0], indices[0]):
        if idx != -1:
            semantic_scores[idx] = float(score)
    return normalize_scores(semantic_scores)


def bm25_scores(query: str, metadata: list[dict]) -> np.ndarray:
    """Calcule un score BM25 simplifie pour chaque passage."""
    query_terms = tokenize(query)
    if not query_terms:
        return np.zeros(len(metadata), dtype="float32")

    documents = [tokenize(item["text_preview"]) for item in metadata]
    avg_doc_len = sum(len(doc) for doc in documents) / max(len(documents), 1)
    doc_freq = {}
    for doc in documents:
        for term in set(doc):
            doc_freq[term] = doc_freq.get(term, 0) + 1

    k1 = 1.5
    b = 0.75
    total_docs = len(documents)
    scores = []
    for doc in documents:
        term_counts = {}
        for term in doc:
            term_counts[term] = term_counts.get(term, 0) + 1

        doc_len = len(doc) or 1
        score = 0.0
        for term in query_terms:
            if term not in term_counts:
                continue
            df = doc_freq.get(term, 0)
            idf = math.log(1 + ((total_docs - df + 0.5) / (df + 0.5)))
            tf = term_counts[term]
            denominator = tf + k1 * (1 - b + b * (doc_len / max(avg_doc_len, 1)))
            score += idf * ((tf * (k1 + 1)) / denominator)
        scores.append(score)

    return normalize_scores(np.array(scores, dtype="float32"))


def tfidf_scores(query: str, metadata: list[dict]) -> np.ndarray:
    """Repli lexical si l'embedding local n'est pas disponible."""
    corpus = [item["text_preview"] for item in metadata]
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode", lowercase=True)
    matrix = vectorizer.fit_transform(corpus)
    query_vector = vectorizer.transform([query])
    return normalize_scores(cosine_similarity(query_vector, matrix)[0].astype("float32"))


def tokenize(text: str) -> list[str]:
    """Tokenisation simple compatible francais sans dependance externe."""
    return re.findall(r"\w+", text.lower())


def normalize_scores(scores: np.ndarray) -> np.ndarray:
    """Ramene les scores entre 0 et 1."""
    if len(scores) == 0:
        return scores
    min_score = float(np.min(scores))
    max_score = float(np.max(scores))
    if max_score == min_score:
        return np.ones_like(scores, dtype="float32") if max_score > 0 else np.zeros_like(scores, dtype="float32")
    return ((scores - min_score) / (max_score - min_score)).astype("float32")


def normalize_mode(mode: str) -> str:
    mode = (mode or "hybrid").lower()
    if mode not in {"semantic", "keyword", "hybrid"}:
        return "hybrid"
    return mode


def normalize_weights(semantic_weight: float, keyword_weight: float, mode: str) -> tuple[float, float]:
    if mode == "semantic":
        return 1.0, 0.0
    if mode == "keyword":
        return 0.0, 1.0

    semantic_weight = max(0.0, float(semantic_weight))
    keyword_weight = max(0.0, float(keyword_weight))
    total = semantic_weight + keyword_weight
    if total == 0:
        return 0.7, 0.3
    return semantic_weight / total, keyword_weight / total


if __name__ == "__main__":
    query = "recherche sur les ressources de peche"
    results = search(query, top_k=3, mode="hybrid")

    print(f'Requete : "{query}"\n')
    for i, result in enumerate(results, start=1):
        print(
            f"{i}. {result['filename']} / passage {result['chunk_id']} "
            f"(score: {result['score']:.4f})"
        )
        print(f"   {result['text_preview'][:160]}...\n")
