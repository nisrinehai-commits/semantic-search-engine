"""
Construit l'index d'embeddings FAISS pour tous les passages extraits.
"""

import json
from pathlib import Path

import faiss
import numpy as np

from src.embeddings.chunking import split_into_chunks
from src.embeddings.embedder import generate_embedding

PROCESSED_DIR = "data/processed"
EMBEDDINGS_DIR = "data/embeddings"


def build_index(
    processed_dir: str = PROCESSED_DIR,
    output_dir: str = EMBEDDINGS_DIR,
    allow_model_download: bool = True,
) -> None:
    """
    Genere les embeddings de tous les passages .txt, construit un index
    FAISS, et sauvegarde l'index ainsi que les metadonnees associees.
    """
    input_path = Path(processed_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    txt_files = sorted(input_path.glob("*.txt"))

    if not txt_files:
        print(f"[WARNING] Aucun fichier .txt trouve dans {processed_dir}")
        return

    embeddings = []
    metadata = []

    for file in txt_files:
        print(f"Encodage de : {file.name}")
        text = file.read_text(encoding="utf-8")
        chunks = split_into_chunks(text)

        for chunk in chunks:
            vector = generate_embedding(chunk.text, allow_download=allow_model_download)
            embeddings.append(vector)
            metadata.append(
                {
                    "filename": file.name,
                    "source_type": _source_type_from_filename(file.name),
                    "chunk_id": chunk.chunk_id,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                    "text_preview": chunk.text[:500],
                    "text_length": len(chunk.text),
                }
            )

    if not embeddings:
        print("[WARNING] Aucun passage exploitable trouve.")
        return

    embeddings_matrix = np.array(embeddings).astype("float32")

    # Avec des vecteurs normalises, le produit scalaire equivaut au cosinus.
    faiss.normalize_L2(embeddings_matrix)

    dimension = embeddings_matrix.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings_matrix)

    faiss.write_index(index, str(output_path / "faiss_index.bin"))
    np.save(output_path / "embeddings.npy", embeddings_matrix)

    with open(output_path / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    stats = {
        "documents": len(txt_files),
        "chunks": len(metadata),
        "dimension": dimension,
        "index_type": "FAISS IndexFlatIP / cosine similarity",
    }
    with open(output_path / "stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"\n[INFO] {len(txt_files)} documents encodes.")
    print(f"[INFO] {len(metadata)} passages indexes.")
    print(f"[INFO] Index FAISS construit : {index.ntotal} vecteurs, dimension {dimension}")
    print(f"[INFO] Sauvegarde dans {output_path}/")


def _source_type_from_filename(filename: str) -> str:
    stem = Path(filename).stem
    suffix = stem.rsplit("_", 1)[-1].lower()
    return suffix if suffix in {"pdf", "docx", "txt"} else "unknown"


if __name__ == "__main__":
    build_index()
