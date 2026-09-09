# Semantic Search Engine - INRH

## Vue d’ensemble

Ce projet est un prototype de moteur de recherche documentaire intelligent conçu pour explorer une solution de gestion documentaire (GED) pilotée par la recherche sémantique et l’IA locale.

L’objectif principal est de permettre à un utilisateur de chercher des informations dans des documents longs et hétérogènes, même quand les mots exacts ne sont pas présents dans le texte. Le système combine :

- extraction de texte depuis plusieurs formats de documents,
- segmentation en passages,
- embeddings vectoriels,
- indexation avec FAISS,
- recherche hybride (sémantique + lexical),
- interface web pour consultation et gestion documentaire.

Ce projet a été conçu dans un contexte de démonstration de preuve de concept, avec un accent sur la recherche par passages, la recherche documentaire intelligente et le workflow documentaire.

---

## Fonctionnalités principales

- Ingestion de documents PDF, DOCX et TXT
- Extraction automatique du texte selon le format source
- Découpage des documents en passages courts et chevauchants
- Génération d’embeddings sémantiques avec un modèle de type sentence-transformers
- Indexation vectorielle avec FAISS
- Recherche hybride : sémantique, lexicale ou mixte
- API REST FastAPI avec endpoints de gestion et de recherche
- Gestion documentaire avec métadonnées, catégories, tags et statut
- Workflow documentaire avec historique d’actions
- Tableau de bord GED pour synthèse globale
- Gestion des versions de document
- Gestion de la corbeille / suppression logique
- Analyse locale du document : résumé, mots-clés, catégorie suggérée, confidentialité
- Assistant documentaire de type RAG local
- Gestion d’utilisateurs et permissions de démonstration
- Authentification JWT en mode démonstration
- Support SQLite par défaut et PostgreSQL en option

---

## Architecture du projet

```text
.
├── data/
│   ├── raw/                  # documents sources
│   ├── processed/            # textes extraits
│   ├── embeddings/          # index FAISS + métadonnées + stats
│   └── metadata/            # SQLite/JSON metadata + workflow + versions
├── src/
│   ├── api/                 # API FastAPI, schémas, bootstrap
│   ├── config.py            # configuration centralisée
│   ├── embeddings/          # embeddings, indexation, chunking
│   ├── ingestion/           # extraction PDF / DOCX / TXT / OCR
│   ├── search/              # moteur de recherche
│   └── utils/               # utilitaires
├── static/
│   └── index.html           # interface web
├── tests/
│   └── *.py                 # tests de l’API et du moteur
├── .gitignore
├── .env.example
├── requirements.txt
├── README.md
├── benchmark.py
└── benchmark_results.json
```

---

## Stack technique

- Python 3.11+
- FastAPI
- FAISS
- NumPy
- scikit-learn
- python-docx
- pypdf
- pytesseract
- pdf2image
- SQLite (par défaut)
- PostgreSQL (optionnel via variable d’environnement)
- Pytest

---

## Installation

### 1. Créer un environnement virtuel

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configurer les variables d’environnement

Un fichier d’exemple est fourni dans [.env.example](.env.example).

Par exemple :

```bash
set GED_JWT_SECRET=une-cle-secrete-longue
set GED_JWT_EXPIRES_SECONDS=86400
set GED_ALLOWED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
```

Pour PostgreSQL :

```bash
set GED_DATABASE_URL=postgresql://ged_user:ged_password@localhost:5432/ged_inrh
```

### 4. Préparer les données

Le projet crée automatiquement les fichiers et tables nécessaires au démarrage, mais il faut aussi construire l’index vectoriel au moins une fois.

---

## Utilisation

### Démarrer l’API

```bash
uvicorn src.api.main:app --reload
```

### Accès à l’interface

```text
http://127.0.0.1:8000/app
```

### Accès à la documentation OpenAPI

```text
http://127.0.0.1:8000/docs
```

### Construire l’index de recherche

```bash
python -m src.embeddings.build_index
```

Cela produit les fichiers suivants dans `data/embeddings/` :

- `faiss_index.bin`
- `embeddings.npy`
- `metadata.json`
- `stats.json`

---

## Points forts du moteur de recherche

### Recherche par passages

La recherche ne se fait pas uniquement sur le document entier, mais sur des passages textuels. Cela permet :

- plus de précision,
- meilleure pertinence des résultats,
- affichage d’extraits utiles,
- meilleur alignement avec une logique de RAG ou d’assistant documentaire.

### Recherche hybride

Le moteur permet trois modes :

- `semantic` : score vectoriel uniquement
- `keyword` : score lexical uniquement
- `hybrid` : combinaison pondérée des deux

La combinaison est généralement de la forme :

```text
score_final = poids_semantique * score_semantique + poids_lexical * score_lexical
```

Par défaut :

```text
0.7 * score_semantique + 0.3 * score_lexical
```

---

## API principale

### Endpoints utiles

| Méthode | Route | Description |
|---|---|---|
| GET | `/` | Vérification simple de l’API |
| GET | `/health` | État de santé |
| GET | `/stats` | Statistiques de l’index |
| GET | `/dashboard` | Indicateurs GED |
| GET | `/documents` | Liste des documents |
| GET | `/documents/{filename}/preview` | Prévisualisation |
| GET | `/documents/{filename}/download` | Téléchargement |
| GET | `/documents/{filename}/metadata` | Métadonnées |
| PUT | `/documents/{filename}/metadata` | Mise à jour des métadonnées |
| GET | `/documents/{filename}/workflow` | Historique workflow |
| POST | `/documents/{filename}/workflow` | Changement de statut |
| DELETE | `/documents/{filename}` | Suppression logique |
| POST | `/documents/{filename}/restore` | Restauration |
| GET | `/documents/{filename}/versions` | Historique des versions |
| GET | `/documents/{filename}/similar` | Documents proches |
| GET | `/documents/{filename}/ai` | Analyse locale IA |
| POST | `/assistant/ask` | Assistant documentaire |
| GET | `/users` | Utilisateurs et permissions |
| POST | `/auth/login` | Connexion demo |
| POST | `/search` | Recherche semantique |
| POST | `/upload?filename=...` | Import et indexation |

### Exemple de requête de recherche

```json
{
  "query": "ressources halieutiques et peche durable",
  "top_k": 5,
  "mode": "hybrid",
  "semantic_weight": 0.7,
  "keyword_weight": 0.3
}
```

---

## Données et persistance

Le projet utilise par défaut une base SQLite locale, créée automatiquement au démarrage dans `data/metadata/`.

Les tables principales sont :

- `document_metadata`
- `workflow_actions`
- `document_versions`
- `users`

Cela permet un démarrage rapide sans dépendance externe, tout en gardant une évolution possible vers PostgreSQL.

---

## Tests

La suite de tests couvre les points clés de l’API et du moteur de recherche.

Pour lancer les tests :

```bash
python -m pytest -q
```

État actuel du projet : les tests passent.

---

## Points d’amélioration recommandés

Le projet est fonctionnel et démonstratif, mais plusieurs améliorations seraient utiles pour le rendre plus professionnel :

- séparer davantage la logique API par domaines (documents, auth, workflow, search)
- centraliser mieux la configuration en environnement
- nettoyer plus strictement les données runtime du dépôt
- renforcer la sécurité des uploads et des permissions
- ajouter CI, lint et type checking
- introduire des migrations de base de données plus robustes
- répartir les responsabilités dans des services métier plus clairs

---

## Exemple de démarrage rapide

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m src.embeddings.build_index
uvicorn src.api.main:app --reload
```

Puis ouvrir :

```text
http://127.0.0.1:8000/app
```

---

## Conclusion

Ce projet montre une preuve de concept solide pour une GED intelligente basée sur la recherche documentaire sémantique. Il est déjà utile pour :

- démontrer un moteur de recherche documentaire intelligent,
- explorer les usages RAG locaux,
- gérer un workflow documentaire simple,
- présenter une architecture de recherche sur documents d’entreprise.

Le prochain niveau de maturité serait d’ajouter une vraie séparation des responsabilités, un meilleur découpage des services et une préparation plus explicite pour un environnement de production.

- recherche par nom de document ;
- filtre par type de fichier ;
- tri par date, nom, taille ou type ;
- pagination ;
- previsualisation integree ;
- telechargement du document original.
- edition des metadonnees depuis le panneau de previsualisation.

Exemple API :

```bash
curl "http://127.0.0.1:8000/documents?file_type=PDF&sort_by=date_desc&page=1&per_page=8"
```

### Metadonnees GED

Chaque document peut recevoir des metadonnees utiles pour une GED :

- categorie ;
- auteur ou service ;
- description ;
- tags ;
- statut documentaire.

Ces informations sont stockees dans `data/metadata/document_metadata.json`.
Ce choix reste simple pour le prototype, tout en preparant une evolution future
vers PostgreSQL et SQLAlchemy.

Exemple API :

```bash
curl -X PUT "http://127.0.0.1:8000/documents/rapport.txt/metadata" \
  -H "Content-Type: application/json" \
  -d "{\"category\":\"Recherche\",\"author\":\"INRH\",\"description\":\"Rapport scientifique\",\"tags\":[\"peche\",\"rapport\"],\"status\":\"Approuve\"}"
```

### Workflow documentaire

Le prototype integre un workflow simple avec les etats suivants :

```text
Brouillon -> Soumis -> En validation -> Approuve -> Archive
                         |
                         -> Rejete
```

Chaque transition enregistre :

- l'ancien statut ;
- le nouveau statut ;
- un commentaire ;
- l'acteur ;
- la date de l'action.

L'historique est stocke dans `data/metadata/workflow_history.json`.

Exemple API :

```bash
curl -X POST "http://127.0.0.1:8000/documents/rapport.txt/workflow" \
  -H "Content-Type: application/json" \
  -d "{\"status\":\"Soumis\",\"comment\":\"Document pret pour validation\",\"actor\":\"Employe demo\"}"
```

### Dashboard GED

Le dashboard consolide les donnees documentaires pour donner une vue de pilotage :

- nombre total de documents ;
- taille totale stockee ;
- documents indexes ;
- documents en attente ;
- repartition par type de fichier ;
- repartition par categorie ;
- repartition par statut ;
- documents recents ;
- activite workflow recente.

Exemple API :

```bash
curl "http://127.0.0.1:8000/dashboard"
```

### IA documentaire et assistant

Le prototype ajoute une couche IA explicable, sans dependance cloud obligatoire :

- resume automatique extractif ;
- extraction de mots-cles ;
- suggestion de categorie documentaire ;
- estimation simple de confidentialite ;
- detection de documents similaires ou doublons ;
- assistant documentaire qui s'appuie sur la recherche hybride et cite les passages sources.

Exemples API :

```bash
curl "http://127.0.0.1:8000/documents/rapport.txt/ai"
```

```bash
curl -X POST "http://127.0.0.1:8000/assistant/ask" \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"Quels documents parlent de peche durable ?\",\"top_k\":5}"
```

Cette approche est adaptee a un prototype PFE car elle reste reproductible,
locale et compatible avec des documents sensibles. Une evolution entreprise
pourrait remplacer la generation extractive par un LLM interne ou un service
RAG securise.

### Corbeille, versions et utilisateurs

La GED integre maintenant :

- une suppression logique qui conserve le fichier original ;
- une restauration depuis la corbeille ;
- une gestion de versions basee sur l'empreinte SHA-256 du fichier ;
- des utilisateurs de demonstration avec roles et permissions :
  Administrateur, Responsable qualite, Validateur et Employe.
- une authentification JWT pour les actions protegees ;
- des permissions par document via le champ `allowed_roles`.

Comptes de demonstration :

| Email | Mot de passe | Role |
|---|---|---|
| `admin@inrh.demo` | `demo123` | Administrateur |
| `qualite@inrh.demo` | `demo123` | Responsable qualite |
| `validateur@inrh.demo` | `demo123` | Validateur |
| `employe@inrh.demo` | `demo123` | Employe |

Exemple de connexion :

```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@inrh.demo\",\"password\":\"demo123\"}"
```

Pour appeler une route protegee, ajouter le token :

```bash
curl -X PUT "http://127.0.0.1:8000/documents/rapport.txt/metadata" \
  -H "Authorization: Bearer VOTRE_TOKEN_JWT" \
  -H "Content-Type: application/json" \
  -d "{\"category\":\"Recherche\",\"tags\":[\"peche\"],\"status\":\"Indexe\",\"folder\":\"/Recherche\",\"allowed_roles\":[\"Validateur\"]}"
```

Si `allowed_roles` est vide, le document reste lisible pour tous les utilisateurs
autorises a acceder a la GED. Si une liste de roles est definie, seuls ces roles
et l'administrateur peuvent consulter le document.

## Modele utilise

Le prototype utilise `paraphrase-multilingual-MiniLM-L12-v2`, un modele SBERT
multilingue compatible avec le francais. Les vecteurs ont une dimension de 384.

## Tests

```bash
python -m pytest tests/ -v
```

## Pistes d'evolution

- Ajouter Alembic pour versionner les migrations SQL.
- Brancher l'authentification sur LDAP/Active Directory.
- Workflow multi-niveaux parametrable selon le type documentaire.
- Preview PDF enrichie avec annotations et surlignage du passage retrouve.
- Knowledge Graph documentaire pour visualiser les themes, services et liens entre documents.
- Integration optionnelle avec SharePoint, LDAP/Active Directory ou un stockage objet.

## Statut

Version de demonstration prete : pipeline complet Documents -> Extraction ->
Passages -> SBERT -> FAISS -> API REST -> Interface web.
