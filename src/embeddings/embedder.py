"""
Module de génération d'embeddings sémantiques via SBERT.
"""

from sentence_transformers import SentenceTransformer

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

# Le modèle est chargé une seule fois au niveau module, pas à chaque appel
# de fonction : le chargement est coûteux (plusieurs secondes), on ne veut
# pas le refaire à chaque texte à encoder.
_model = None


def get_model() -> SentenceTransformer:
    """
    Charge le modèle SBERT (une seule fois, mis en cache en mémoire).
    """
    global _model
    if _model is None:
        print(f"[INFO] Chargement du modèle SBERT : {MODEL_NAME} ...")
        _model = SentenceTransformer(MODEL_NAME)
        print("[INFO] Modèle chargé.")
    return _model


def generate_embedding(text: str):
    """
    Génère l'embedding (vecteur) d'un texte donné.

    Args:
        text: le texte à encoder

    Returns:
        Un vecteur numpy de dimension 384.
    """
    model = get_model()
    embedding = model.encode(text)
    return embedding


if __name__ == "__main__":
    sample_text = "Le Département mène des recherches sur les ressources halieutiques."
    vector = generate_embedding(sample_text)
    print(f"--- Texte : {sample_text}")
    print(f"--- Dimension du vecteur : {vector.shape}")
    print(f"--- 10 premières valeurs : {vector[:10]}")