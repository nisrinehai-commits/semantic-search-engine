# Moteur de Recherche Sémantique — INRH

## Contexte
Projet réalisé dans le cadre d'un stage à l'INRH (Institut National de Recherche Halieutique),
département Système d'Information, en vue d'une intégration future dans une plateforme GED.

## Objectif
Développer un moteur de recherche sémantique basé sur SBERT (Sentence-BERT) capable de :
- indexer un ensemble de documents,
- générer des embeddings sémantiques,
- calculer la similarité entre une requête et les documents,
- retourner les documents les plus pertinents.

## Roadmap
- [x] Setup initial du projet
- [x] Étape 2 : Ingestion de documents (DOCX, PDF natif, PDF scanné via OCR)
- [x] Étape 3 : Génération d'embeddings avec SBERT
- [x] V1 : Recherche sémantique par similarité cosinus
- [x] V2 : Intégration FAISS pour la recherche vectorielle ✅
- [ ] V3 : API + interface utilisateur
- [ ] V4 : Intégration RAG / assistant documentaire

## Recherche vectorielle
La recherche s'appuie sur [FAISS](https://github.com/facebookresearch/faiss) (Facebook AI
Similarity Search), avec un index `IndexFlatIP` sur vecteurs normalisés L2 (équivalent à une
similarité cosinus, mais optimisé pour passer à l'échelle sur un grand volume de documents).

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
│   └── build_index.py       # Indexation en masse (data/processed -> data/embeddings)
├── search/
│   └── search_engine.py     # Recherche par similarité cosinus (Top-K)
└── utils/
\`\`\`

## Utilisation (pipeline complet)
\`\`\`bash
# 1. Extraire le texte des documents (data/raw -> data/processed)
python -m src.ingestion.loader

# 2. Générer les embeddings (data/processed -> data/embeddings)
python -m src.embeddings.build_index

# 3. Rechercher (exemple dans le fichier, modifiable)
python -m src.search.search_engine
\`\`\`

## Modèle utilisé
[paraphrase-multilingual-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
— modèle SBERT multilingue (50+ langues dont le français), vecteurs de dimension 384.

## Prérequis système (Windows)
En plus des dépendances Python (\`requirements.txt\`), ce projet nécessite :
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) (avec le pack de langue française)
- [Poppler](https://github.com/oschwartz10612/poppler-windows/releases/) (ajouté au PATH)

## Tests
\`\`\`bash
python -m pytest tests/ -v
\`\`\`

## Installation
\`\`\`bash
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
\`\`\`

## Statut
🚧 En cours de développement — Étape 1 : initialisation du projet.