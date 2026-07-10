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
- [ ] Étape 3 : Génération d'embeddings avec SBERT
- [ ] V1 : Recherche sémantique par similarité cosinus
- [ ] V2 : Intégration FAISS pour la recherche vectorielle
- [ ] V3 : API + interface utilisateur
- [ ] V4 : Intégration RAG / assistant documentaire

## Structure du projet
\`\`\`
src/
├── ingestion/          # Extraction de texte (DOCX, PDF, OCR)
│   ├── docx_extractor.py
│   ├── pdf_extractor.py
│   ├── ocr_extractor.py
│   └── loader.py        # Orchestrateur (détection format + fallback OCR)
├── embeddings/          # (à venir) Génération d'embeddings SBERT
├── search/              # (à venir) Similarité et recherche
└── utils/
\`\`\`

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