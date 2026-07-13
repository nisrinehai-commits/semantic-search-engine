"""
Moteur de recherche sémantique : compare une requête aux documents indexés
via FAISS (recherche vectorielle optimisée).
"""

import json
from pathlib import Path

import faiss
import numpy as np

from src.embeddings.embedder import generate_embedding

EMBEDDINGS_DIR = "data/embeddings"


def load_index(embeddings_dir: str = EMBEDDINGS_DIR):
    """
    Charge l'index FAISS et les métadonnées associées.

    Returns:
        Tuple (index_faiss, metadata_list)
    """
    index_path = Path(embeddings_dir) / "faiss_index.bin"
    metadata_path = Path(embeddings_dir) / "metadata.json"

    if not index_path.exists() or not metadata_path.exists():
        raise FileNotFoundError(
            "Index introuvable. Lance d'abord : python -m src.embeddings.build_index"
        )

    index = faiss.read_index(str(index_path))
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    return index, metadata


def search(query: str, top_k: int = 3, embeddings_dir: str = EMBEDDINGS_DIR):
    """
    Recherche les documents les plus pertinents pour une requête donnée,
    via l'index FAISS.

    Args:
        query: la requête en langage naturel
        top_k: nombre de résultats à retourner
        embeddings_dir: dossier contenant l'index

    Returns:
        Liste de dicts triés par pertinence décroissante :
        [{"filename": ..., "score": ..., "text_preview": ...}, ...]
    """
    index, metadata = load_index(embeddings_dir)

    query_vector = generate_embedding(query).astype("float32").reshape(1, -1)
    faiss.normalize_L2(query_vector)

    scores, indices = index.search(query_vector, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue  # FAISS retourne -1 si moins de top_k résultats existent
        results.append({
            "filename": metadata[idx]["filename"],
            "score": float(score),
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