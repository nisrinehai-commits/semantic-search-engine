"""
Construit l'index d'embeddings pour tous les documents traités.
"""

import json
from pathlib import Path

import numpy as np

from src.embeddings.embedder import generate_embedding

PROCESSED_DIR = "data/processed"
EMBEDDINGS_DIR = "data/embeddings"


def build_index(processed_dir: str = PROCESSED_DIR, output_dir: str = EMBEDDINGS_DIR) -> None:
    """
    Génère et sauvegarde les embeddings de tous les fichiers .txt
    présents dans processed_dir.
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

    embeddings_matrix = np.array(embeddings)

    np.save(output_path / "embeddings.npy", embeddings_matrix)
    with open(output_path / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"\n[INFO] {len(txt_files)} documents encodés.")
    print(f"[INFO] Matrice d'embeddings : {embeddings_matrix.shape}")
    print(f"[INFO] Sauvegardé dans {output_path}/")


if __name__ == "__main__":
    build_index()
    