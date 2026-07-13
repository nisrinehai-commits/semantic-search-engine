# Moteur de Recherche Sémantique — INRH

## Contexte
Projet réalisé dans le cadre d'un stage à l'INRH (Institut National de Recherche Halieutique),
département Système d'Information, en vue d'une intégration future dans une plateforme GED.

## Objectif
Développer un moteur de recherche sémantique basé sur SBERT (Sentence-BERT) capable de :
- indexer un ensemble de documents (DOCX, PDF natif, PDF scanné),
- générer des embeddings sémantiques,
- calculer la similarité entre une requête et les documents via une recherche vectorielle (FAISS),
- retourner les documents les plus pertinents,
- être exposé via une API REST.

## Roadmap
- [x] Setup initial du projet
- [x] Ingestion de documents (DOCX, PDF natif, PDF scanné via OCR)
- [x] Génération d'embeddings avec SBERT
- [x] V1 : Recherche sémantique par similarité cosinus
- [x] V2 : Intégration FAISS pour la recherche vectorielle
- [x] V3 : API REST (FastAPI)
- [ ] V4 : Intégration RAG / assistant documentaire

## Structure du projet
\`\`\`
src/
├── ingestion/
│   ├── docx_extractor.py    # Extraction DOCX
│   ├── pdf_extractor.py     # Extraction PDF natif
│   ├── ocr_extractor.py     # Extraction PDF scanné (OCR)
│   └── loader.py            # Orchestrateur (détection format + fallback OCR)
├── embeddings/
│   ├── embedder.py          # Génération d'un embedding SBERT
│   └── build_index.py       # Indexation en masse (data/processed -> data/embeddings, index FAISS)
├── search/
│   └── search_engine.py     # Recherche vectorielle (FAISS) Top-K
├── api/
│   ├── main.py               # Endpoints FastAPI (/, /health, /search)
│   └── schemas.py            # Schémas Pydantic (requêtes/réponses)
└── utils/
\`\`\`

## Installation
\`\`\`bash
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
\`\`\`

### Prérequis système (Windows)
En plus des dépendances Python (\`requirements.txt\`), ce projet nécessite :
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) (avec le pack de langue française), ajouté au PATH
- [Poppler](https://github.com/oschwartz10612/poppler-windows/releases/), ajouté au PATH

## Utilisation

### Pipeline en ligne de commande
\`\`\`bash
# 1. Extraire le texte des documents (data/raw -> data/processed)
python -m src.ingestion.loader

# 2. Générer les embeddings et l'index FAISS (data/processed -> data/embeddings)
python -m src.embeddings.build_index

# 3. Rechercher (exemple dans le fichier, modifiable)
python -m src.search.search_engine
\`\`\`

### API REST
\`\`\`bash
uvicorn src.api.main:app --reload
\`\`\`
Documentation interactive une fois le serveur lancé : http://127.0.0.1:8000/docs

| Méthode | Route | Description |
|---|---|---|
| GET | \`/\` | Vérifie que l'API tourne |
| GET | \`/health\` | Endpoint de santé |
| POST | \`/search\` | Recherche sémantique (body: \`{"query": "...", "top_k": 3}\`) |

## Modèle utilisé
[paraphrase-multilingual-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
— modèle SBERT multilingue (50+ langues dont le français), vecteurs de dimension 384.

## Recherche vectorielle
La recherche s'appuie sur [FAISS](https://github.com/facebookresearch/faiss) (Facebook AI
Similarity Search), avec un index \`IndexFlatIP\` sur vecteurs normalisés L2 (équivalent à une
similarité cosinus, mais optimisé pour passer à l'échelle sur un grand volume de documents).

## Tests
\`\`\`bash
python -m pytest tests/ -v
\`\`\`

## Statut
✅ V3 fonctionnelle : pipeline complet Documents -> Extraction -> SBERT -> FAISS -> API REST.