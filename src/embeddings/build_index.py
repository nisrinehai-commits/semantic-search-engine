"""
Construit l'index d'embeddings (FAISS) pour tous les documents traités.
"""

import json
from pathlib import Path

import faiss
import numpy as np

from src.embeddings.embedder import generate_embedding

PROCESSED_DIR = "data/processed"
EMBEDDINGS_DIR = "data/embeddings"


def build_index(processed_dir: str = PROCESSED_DIR, output_dir: str = EMBEDDINGS_DIR) -> None:
    """
    Génère les embeddings de tous les fichiers .txt, construit un index
    FAISS, et sauvegarde l'index ainsi que les métadonnées associées.
    """
    input_path = Path(processed_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    txt_files = sorted(input_path.glob("*.txt"))

    if not txt_files:
        print(f"[WARNING] Aucun fichier .txt trouvé dans {processed_dir}")
        return

    embeddings = []
    metadata = []

    for file in txt_files:
        print(f"Encodage de : {file.name}")
        text = file.read_text(encoding="utf-8")
        vector = generate_embedding(text)

        embeddings.append(vector)
        metadata.append({
            "filename": file.name,
            "text_preview": text[:200],
        })

    embeddings_matrix = np.array(embeddings).astype("float32")

    # Normalisation L2 : indispensable pour que le produit scalaire (IP)
    # de FAISS soit équivalent à une similarité cosinus.
    faiss.normalize_L2(embeddings_matrix)

    dimension = embeddings_matrix.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings_matrix)

    faiss.write_index(index, str(output_path / "faiss_index.bin"))
    with open(output_path / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"\n[INFO] {len(txt_files)} documents encodés.")
    print(f"[INFO] Index FAISS construit : {index.ntotal} vecteurs, dimension {dimension}")
    print(f"[INFO] Sauvegardé dans {output_path}/")


if __name__ == "__main__":
    build_index()