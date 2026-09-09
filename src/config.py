from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_VERSION = "1.1.0"
DATA_DIR = PROJECT_ROOT / "data"
EMBEDDINGS_DIR = str(DATA_DIR / "embeddings")
RAW_DIR = str(DATA_DIR / "raw")
PROCESSED_DIR = str(DATA_DIR / "processed")
METADATA_PATH = str(DATA_DIR / "metadata" / "document_metadata.json")
WORKFLOW_LOG_PATH = str(DATA_DIR / "metadata" / "workflow_history.json")
VERSIONS_PATH = str(DATA_DIR / "metadata" / "document_versions.json")
USERS_PATH = str(DATA_DIR / "metadata" / "users.json")

SUPPORTED_UPLOAD_EXTENSIONS = {".pdf", ".docx", ".txt"}
WORKFLOW_STEPS = ["Brouillon", "Soumis", "En validation", "Approuve", "Rejete", "Archive"]
JWT_SECRET = os.getenv("GED_JWT_SECRET", "change-this-secret-for-production")
JWT_EXPIRES_SECONDS = int(os.getenv("GED_JWT_EXPIRES_SECONDS", "86400"))

DEFAULT_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
    "http://127.0.0.1:8010",
    "http://127.0.0.1:8011",
    "http://127.0.0.1:8012",
    "http://127.0.0.1:8013",
    "http://127.0.0.1:8014",
    "http://127.0.0.1:8015",
    "http://127.0.0.1:8016",
    "http://127.0.0.1:8017",
    "http://127.0.0.1:8018",
    "http://127.0.0.1:8019",
    "http://localhost:8000",
    "http://localhost:8015",
    "http://localhost:8016",
    "http://localhost:8017",
    "http://localhost:8018",
    "http://localhost:8019",
    "null",
]


def get_allowed_origins() -> list[str]:
    raw_value = os.getenv("GED_ALLOWED_ORIGINS")
    if raw_value:
        origins = [origin.strip() for origin in raw_value.split(",") if origin.strip()]
        return origins or DEFAULT_ALLOWED_ORIGINS
    return DEFAULT_ALLOWED_ORIGINS


PUBLIC_READ_USER = {
    "id": "anonymous",
    "name": "Visiteur local",
    "email": "anonymous@local",
    "role": "Employe",
    "permissions": ["documents:read", "search:read"],
}

FRENCH_STOPWORDS = {
    "avec", "dans", "des", "du", "elle", "est", "les", "leur", "leurs", "nous",
    "par", "pas", "pour", "que", "qui", "sur", "une", "vous", "aux", "ces",
    "cette", "comme", "document", "documents", "rapport", "entre", "plus",
    "afin", "ainsi", "sont", "etre", "son", "ses", "the", "and", "for",
}

CATEGORY_RULES = {
    "Peche": {"peche", "halieutique", "ressources", "maritime", "poisson"},
    "Aquaculture": {"aquaculture", "production", "elevage", "marine", "larves"},
    "Qualite": {"qualite", "norme", "validation", "procedure", "audit"},
    "RH": {"rh", "ressources", "humaines", "salaire", "conge", "employe"},
    "Finance": {"finance", "budget", "facture", "paiement", "cout", "achat"},
    "Informatique": {"informatique", "systeme", "donnees", "securite", "serveur"},
}

APP_ALLOWED_ORIGINS = get_allowed_origins()
VERSION = APP_VERSION
