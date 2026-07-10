"""
Moteur de recherche sémantique : compare une requête aux documents indexés
via la similarité cosinus.
"""

import json
from pathlib import Path

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from src.embeddings.embedder import generate_embedding

EMBEDDINGS_DIR = "data/embeddings"


def load_index(embeddings_dir: str = EMBEDDINGS_DIR):
    """
    Charge la matrice d'embeddings et les métadonnées associées.

    Returns:
        Tuple (embeddings_matrix, metadata_list)
    """
    embeddings_path = Path(embeddings_dir) / "embeddings.npy"
    metadata_path = Path(embeddings_dir) / "metadata.json"

    if not embeddings_path.exists() or not metadata_path.exists():
        raise FileNotFoundError(
            "Index introuvable. Lance d'abord : python -m src.embeddings.build_index"
        )

    embeddings_matrix = np.load(embeddings_path)
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    return embeddings_matrix, metadata


def search(query: str, top_k: int = 3, embeddings_dir: str = EMBEDDINGS_DIR):
    """
    Recherche les documents les plus pertinents pour une requête donnée.

    Args:
        query: la requête en langage naturel
        top_k: nombre de résultats à retourner
        embeddings_dir: dossier contenant l'index

    Returns:
        Liste de dicts triés par pertinence décroissante :
        [{"filename": ..., "score": ..., "text_preview": ...}, ...]
    """
    embeddings_matrix, metadata = load_index(embeddings_dir)

    query_vector = generate_embedding(query).reshape(1, -1)

    similarities = cosine_similarity(query_vector, embeddings_matrix)[0]

    ranked_indices = np.argsort(similarities)[::-1][:top_k]

    results = []
    for idx in ranked_indices:
        results.append({
            "filename": metadata[idx]["filename"],
            "score": float(similarities[idx]),
            "text_preview": metadata[idx]["text_preview"],
        })

    return results


if __name__ == "__main__":
    query = "recherche sur les ressources de pêche"
    results = search(query, top_k=3)

    print(f"Requête : \"{query}\"\n")
    for i, result in enumerate(results, start=1):
        print(f"{i}. {result['filename']}  (score: {result['score']:.4f})")
        print(f"   {result['text_preview'][:120]}...\n")