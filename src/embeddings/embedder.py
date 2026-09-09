"""
Generation d'embeddings semantiques via SBERT.

Le mode principal utilise SBERT. Un repli local deterministe est fourni pour
garder la demo utilisable hors ligne, notamment lors d'un upload depuis l'API.
"""

import hashlib
import re

import numpy as np

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIMENSION = 384

_model = None


def get_model(allow_download: bool = False):
    """
    Charge le modele SBERT une seule fois et privilegie le cache local.

    En environnement de demonstration ou de test, cela evite de dependre du
    reseau a chaque lancement si le modele a deja ete telecharge.
    """
    global _model
    if _model is not None:
        return _model

    print(f"[INFO] Chargement du modele SBERT : {MODEL_NAME} ...")
    try:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(MODEL_NAME, local_files_only=True)
    except Exception:
        if not allow_download:
            raise RuntimeError(
                "Modele SBERT indisponible en cache local. "
                "Lance python -m src.embeddings.build_index avec acces reseau "
                "pour le telecharger."
            )
        _model = SentenceTransformer(MODEL_NAME)
    print("[INFO] Modele charge.")
    return _model


def generate_embedding(text: str, allow_download: bool = False):
    """
    Genere l'embedding d'un texte donne.

    Si SBERT n'est pas accessible en mode sans telechargement, on utilise un
    embedding lexical local. Ce repli n'a pas la richesse semantique de SBERT,
    mais il permet de reconstruire l'index et de tester l'application hors ligne.
    """
    try:
        model = get_model(allow_download=allow_download)
        return model.encode(text)
    except RuntimeError:
        return generate_local_embedding(text)


def generate_local_embedding(text: str, dimension: int = EMBEDDING_DIMENSION):
    """Produit un vecteur local deterministe par hachage de tokens."""
    vector = np.zeros(dimension, dtype="float32")
    tokens = re.findall(r"\w+", text.lower())

    if not tokens:
        return vector

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "little") % dimension
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign

    norm = np.linalg.norm(vector)
    if norm > 0:
        vector /= norm
    return vector


if __name__ == "__main__":
    sample_text = "Le departement mene des recherches sur les ressources halieutiques."
    vector = generate_embedding(sample_text, allow_download=True)
    print(f"--- Texte : {sample_text}")
    print(f"--- Dimension du vecteur : {vector.shape}")
    print(f"--- 10 premieres valeurs : {vector[:10]}")
