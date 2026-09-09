# Prototype de recherche semantique documentaire - INRH

## Contexte

Ce prototype a ete realise dans le cadre d'un stage a l'INRH, avec l'objectif
d'explorer une brique de recherche intelligente pour une future plateforme GED.

L'idee principale est de permettre a un utilisateur de poser une question en
langage naturel et de retrouver les passages documentaires les plus pertinents,
meme si les mots exacts de la requete ne sont pas presents dans le document.

## Fonctionnalites principales

- Ingestion de plusieurs formats : DOCX, PDF natif, PDF scanne via OCR et TXT.
- Extraction automatique du texte selon le type de document.
- Decoupage des documents en passages courts et chevauchants.
- Generation d'embeddings semantiques avec SBERT multilingue.
- Indexation vectorielle avec FAISS.
- Recherche par similarite cosinus sur les passages, pas seulement sur les documents entiers.
- API REST FastAPI avec endpoints de recherche et de statistiques.
- Interface web de demonstration disponible dans le navigateur.
- Upload avance depuis l'interface : drag & drop, multi-fichiers, validation des formats,
  progression et indexation automatique.
- Bibliotheque documentaire : liste des documents, recherche instantanee, filtre par type,
  tri, pagination, vues cartes/tableau, previsualisation et telechargement.
- Gestion de metadonnees GED : categorie, auteur, description, tags et statut documentaire.
- Workflow documentaire : changement d'etat, commentaires, acteur et historique des actions.
- Dashboard GED : indicateurs globaux, repartitions par type/categorie/statut,
  documents recents et activite workflow.
- Recherche hybride : fusion configurable entre score semantique et score mots-cles.
- Corbeille documentaire : suppression logique et restauration.
- Gestion des versions : empreinte SHA-256 et historique des imports.
- Analyse IA locale : resume automatique, mots-cles, categorie suggeree,
  niveau de confidentialite et doublons potentiels.
- Assistant documentaire RAG local : questions-reponses avec citations de passages.
- Gestion utilisateurs de demonstration : roles, permissions et connexion demo.
- Persistance relationnelle : SQLite local par defaut et PostgreSQL activable par configuration.
- Authentification JWT avec mots de passe hashes pour les comptes de demonstration.
- Permissions par document : restriction possible par roles autorises.

## Pourquoi la recherche par passages ?

La premiere version indexait un vecteur par document. Cette approche fonctionne
sur un petit corpus, mais elle devient moins precise quand les documents sont
longs ou contiennent plusieurs sujets.

La version actuelle indexe des passages. Cela permet :

- d'obtenir des resultats plus precis ;
- d'afficher directement l'extrait utile ;
- de preparer plus naturellement une future evolution vers du RAG ou un assistant documentaire.

## Architecture

```text
data/
  raw/          Documents sources
  processed/    Textes extraits
  embeddings/   Index FAISS, embeddings, metadonnees et statistiques

src/
  ingestion/    Extraction DOCX, PDF, OCR et TXT
  embeddings/   Decoupage, embeddings et construction d'index
  search/       Moteur de recherche vectorielle
  api/          API REST FastAPI
static/
  index.html    Interface web de demonstration
tests/
  test_*.py     Tests unitaires
```

## Installation

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Prerequis systeme pour les PDF scannes

Pour l'OCR, installer aussi :

- Tesseract OCR avec le pack de langue francaise ;
- Poppler, ajoute au PATH.

## Utilisation

### 1. Extraire les textes

```bash
python -m src.ingestion.loader
```

### 2. Construire l'index vectoriel

```bash
python -m src.embeddings.build_index
```

La construction produit :

- `data/embeddings/faiss_index.bin`
- `data/embeddings/embeddings.npy`
- `data/embeddings/metadata.json`
- `data/embeddings/stats.json`

### 3. Lancer l'API et l'interface

```bash
uvicorn src.api.main:app --reload
```

Interface web :

```text
http://127.0.0.1:8000/app
```

Documentation interactive FastAPI :

```text
http://127.0.0.1:8000/docs
```

### Configuration base de donnees

Par defaut, le prototype utilise une base SQLite locale creee automatiquement dans
`data/metadata/document_metadata.db`. Cela permet de tester le projet sans installer
PostgreSQL.

Pour utiliser PostgreSQL, definir la variable d'environnement suivante avant de
lancer l'API :

```bash
set GED_DATABASE_URL=postgresql://ged_user:ged_password@localhost:5432/ged_inrh
uvicorn src.api.main:app --reload
```

Les tables sont creees automatiquement au demarrage :

- `document_metadata`
- `workflow_actions`
- `document_versions`
- `users`

Variables utiles :

```bash
set GED_JWT_SECRET=une-cle-secrete-longue
set GED_JWT_EXPIRES_SECONDS=86400
```

## Endpoints API

| Methode | Route | Description |
|---|---|---|
| GET | `/` | Verification simple de l'API |
| GET | `/health` | Etat de sante |
| GET | `/stats` | Statistiques de l'index |
| GET | `/dashboard` | Indicateurs et activite GED |
| GET | `/documents` | Liste paginee des documents |
| GET | `/documents/{filename}/preview` | Previsualisation PDF, DOCX ou TXT |
| GET | `/documents/{filename}/download` | Telechargement du document original |
| GET | `/documents/{filename}/metadata` | Lecture des metadonnees GED |
| PUT | `/documents/{filename}/metadata` | Mise a jour des metadonnees GED |
| GET | `/documents/{filename}/workflow` | Historique de workflow du document |
| POST | `/documents/{filename}/workflow` | Changement d'etat avec commentaire |
| DELETE | `/documents/{filename}` | Suppression logique / corbeille |
| POST | `/documents/{filename}/restore` | Restauration depuis la corbeille |
| GET | `/documents/{filename}/versions` | Historique des versions connues |
| GET | `/documents/{filename}/similar` | Documents similaires ou doublons potentiels |
| GET | `/documents/{filename}/ai` | Resume, mots-cles, classification et confidentialite |
| POST | `/assistant/ask` | Assistant documentaire RAG local |
| GET | `/users` | Utilisateurs, roles et permissions demo |
| POST | `/auth/login` | Connexion de demonstration |
| GET | `/metadata/categories` | Liste des categories utilisees |
| POST | `/search` | Recherche semantique |
| POST | `/upload?filename=...` | Import et indexation automatique d'un document |

Exemple de requete :

```json
{
  "query": "ressources halieutiques et peche durable",
  "top_k": 5,
  "mode": "hybrid",
  "semantic_weight": 0.7,
  "keyword_weight": 0.3
}
```

Exemple de resultat :

```json
{
  "filename": "doc_peche_durable_docx.txt",
  "source_type": "docx",
  "chunk_id": 0,
  "start_char": 0,
  "end_char": 842,
  "score": 0.73,
  "semantic_score": 0.81,
  "keyword_score": 0.54,
  "search_mode": "hybrid",
  "text_preview": "..."
}
```

### Recherche hybride

Le moteur propose trois modes :

- `semantic` : recherche par similarite vectorielle FAISS / embeddings ;
- `keyword` : recherche mots-cles avec un score BM25 simplifie ;
- `hybrid` : fusion des deux scores.

La formule utilisee en mode hybride est :

```text
score_final = poids_semantique * score_semantique + poids_mots_cles * score_BM25
```

Par defaut :

```text
score_final = 0.7 * score_semantique + 0.3 * score_BM25
```

Depuis l'interface, l'utilisateur peut choisir le mode et modifier les poids
avec des curseurs. Les resultats affichent le score final, le score semantique
et le score mots-cles.

### Upload avance

Depuis l'interface web, il est possible de glisser-deposer un ou plusieurs
documents PDF, DOCX ou TXT. Chaque fichier est :

1. valide selon son extension ;
2. sauvegarde dans `data/raw` ;
3. extrait vers `data/processed` ;
4. ajoute a l'index vectoriel ;
5. disponible immediatement dans la recherche.

L'endpoint `/upload` accepte un fichier envoye en binaire brut :

```bash
curl -X POST "http://127.0.0.1:8000/upload?filename=note.txt" \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@note.txt"
```

Si un fichier porte deja le meme nom, le systeme ajoute automatiquement un
suffixe temporel afin de ne pas ecraser l'ancien document.

### Bibliotheque documentaire

La page principale propose une bibliotheque GED avec :

- affichage en cartes ou tableau ;
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
