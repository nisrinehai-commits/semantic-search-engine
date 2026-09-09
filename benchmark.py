"""
Script de benchmark - a executer LOCALEMENT dans le venv du projet
(la ou le modele SBERT et l'index FAISS sont deja disponibles).

USAGE :
    1. Copier ce fichier a la racine du projet (a cote de main.py)
    2. Completer la liste TEST_QUERIES ci-dessous avec de VRAIES requetes
       et les noms de fichiers reellement pertinents dans data/raw
       (remplacer les exemples marques "A ADAPTER")
    3. Lancer :  python benchmark.py
    4. Le script genere :
         - benchmark_results.json   (donnees brutes)
         - benchmark_table.png      (tableau recapitulatif)
         - benchmark_precision_recall.png
         - benchmark_temps_reponse.png
    5. Envoyez ces 4 fichiers pour integration finale dans le rapport.

Le script compare 3 methodes :
    - "semantique"  : recherche vectorielle pure (semantic_weight=1.0)
    - "lexical"     : recherche par mots-cles pure (keyword_weight=1.0)
    - "hybride"     : combinaison ponderee (semantic_weight=0.7, keyword_weight=0.3)
et, si scikit-learn est installe, une baseline TF-IDF independante
(pour illustrer la comparaison avec les approches classiques du chapitre 3).
"""

import json
import time
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. A ADAPTER : vos requetes de test + fichiers reellement pertinents
# ---------------------------------------------------------------------------
# Regle : pour chaque requete, listez le/les noms de fichiers (dans data/raw)
# qui contiennent reellement une reponse pertinente. Visez au moins 8-10
# requetes couvrant differents themes/documents pour un resultat credible.
TEST_QUERIES = [
    {"query": "developpement de l'aquaculture marine et elevage de poissons",
     "expected_files": ["doc_aquaculture_docx.txt"]},
    {"query": "exécution budgétaire et depenses de fonctionnement",
     "expected_files": ["doc_finance_docx.txt"]},
    {"query": "audit reseau et vulnerabilites de securite informatique",
     "expected_files": ["doc_informatique_docx.txt"]},
    {"query": "gestion durable des quotas de peche et stocks de sardines",
     "expected_files": ["doc_peche_durable_docx.txt"]},
    {"query": "politique de teletravail et ressources humaines",
     "expected_files": ["doc_ressources_humaines_docx.txt"]},
    {"query": "extraction de texte pour moteur de recherche semantique",
     "expected_files": ["test_document_docx.txt", "test_document_pdf.txt"]},
    {"query": "ressources halieutiques et techniques de peche",
     "expected_files": ["test_document_docx.txt", "test_document_pdf.txt", "doc_peche_durable_docx.txt"]},
    {"query": "lutte contre l'exclusion et action sociale",
     "expected_files": ["test_document_scan_pdf.txt"]},
    {"query": "stocks sauvages et pression sur les ressources marines",
     "expected_files": ["doc_aquaculture_docx.txt", "doc_peche_durable_docx.txt"]},
    {"query": "mise a jour des postes de travail et pare-feux",
     "expected_files": ["doc_informatique_docx.txt"]},
]

TOP_K = 5
OUTPUT_DIR = Path(".")

# ---------------------------------------------------------------------------
# 2. Verification rapide de la config avant de lancer les vrais tests
# ---------------------------------------------------------------------------
if any(q["query"].startswith("A ADAPTER") for q in TEST_QUERIES):
    print("!! Merci de completer TEST_QUERIES avec de vraies requetes et de vrais")
    print("!! noms de fichiers avant de lancer le benchmark (voir docstring en haut du fichier).")
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from src.search.search_engine import search as engine_search
except Exception as exc:
    print(f"Impossible d'importer src.search.search_engine.search : {exc}")
    print("Verifiez que ce script est bien place a la racine du projet.")
    sys.exit(1)


def precision_recall_at_k(returned_files, expected_files, k):
    top = returned_files[:k]
    relevant_returned = [f for f in top if f in expected_files]
    precision = len(relevant_returned) / max(len(top), 1)
    recall = len(set(relevant_returned)) / max(len(set(expected_files)), 1)
    return precision, recall


def run_engine_method(method_name, semantic_weight, keyword_weight):
    precisions, recalls, times = [], [], []
    for item in TEST_QUERIES:
        t0 = time.perf_counter()
        try:
            raw_results = engine_search(
                item["query"], top_k=TOP_K, mode="hybrid",
                semantic_weight=semantic_weight, keyword_weight=keyword_weight,
            )
        except Exception as exc:
            print(f"[{method_name}] erreur sur la requete '{item['query']}': {exc}")
            continue
        elapsed_ms = (time.perf_counter() - t0) * 1000
        returned_files = [r.get("filename") for r in raw_results]
        p, r_ = precision_recall_at_k(returned_files, item["expected_files"], TOP_K)
        precisions.append(p)
        recalls.append(r_)
        times.append(elapsed_ms)
    n = max(len(precisions), 1)
    return {
        "method": method_name,
        "precision_at_k": round(sum(precisions) / n, 3),
        "recall_at_k": round(sum(recalls) / n, 3),
        "avg_response_time_ms": round(sum(times) / max(len(times), 1), 1),
        "n_queries": len(precisions),
    }


def run_tfidf_baseline():
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError:
        print("scikit-learn non installe : baseline TF-IDF ignoree "
              "(pip install scikit-learn --break-system-packages pour l'activer).")
        return None

    processed_dir = Path("data/processed")
    if not processed_dir.exists():
        print("data/processed introuvable : baseline TF-IDF ignoree.")
        return None

    files, texts = [], []
    for txt_file in processed_dir.glob("*.txt"):
        files.append(txt_file.stem)
        texts.append(txt_file.read_text(encoding="utf-8", errors="ignore"))
    if not texts:
        return None

    vectorizer = TfidfVectorizer(max_features=5000)
    doc_matrix = vectorizer.fit_transform(texts)

    precisions, recalls, times = [], [], []
    for item in TEST_QUERIES:
        t0 = time.perf_counter()
        query_vec = vectorizer.transform([item["query"]])
        sims = cosine_similarity(query_vec, doc_matrix)[0]
        ranked_idx = sims.argsort()[::-1][:TOP_K]
        # map processed stem back to a plausible raw filename (best effort)
        returned_files = [files[i] for i in ranked_idx]
        elapsed_ms = (time.perf_counter() - t0) * 1000
        expected_stems = [Path(f).stem for f in item["expected_files"]]
        p, r_ = precision_recall_at_k(returned_files, expected_stems, TOP_K)
        precisions.append(p)
        recalls.append(r_)
        times.append(elapsed_ms)

    n = max(len(precisions), 1)
    return {
        "method": "tfidf_baseline",
        "precision_at_k": round(sum(precisions) / n, 3),
        "recall_at_k": round(sum(recalls) / n, 3),
        "avg_response_time_ms": round(sum(times) / max(len(times), 1), 1),
        "n_queries": len(precisions),
    }


def main():
    print(f"Lancement du benchmark sur {len(TEST_QUERIES)} requetes, top_k={TOP_K}...\n")

    results = []
    results.append(run_engine_method("semantique", semantic_weight=1.0, keyword_weight=0.0))
    results.append(run_engine_method("lexical", semantic_weight=0.0, keyword_weight=1.0))
    results.append(run_engine_method("hybride", semantic_weight=0.7, keyword_weight=0.3))

    tfidf_result = run_tfidf_baseline()
    if tfidf_result:
        results.append(tfidf_result)

    for r in results:
        print(r)

    with open(OUTPUT_DIR / "benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("\n Resultats bruts sauvegardes -> benchmark_results.json")

    # ---- Graphiques ----
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        methods = [r["method"] for r in results]
        precisions = [r["precision_at_k"] for r in results]
        recalls = [r["recall_at_k"] for r in results]
        times_ms = [r["avg_response_time_ms"] for r in results]

        # Precision / Recall chart
        x = range(len(methods))
        width = 0.35
        fig, ax = plt.subplots(figsize=(7, 4.5))
        ax.bar([i - width/2 for i in x], precisions, width, label=f"Precision@{TOP_K}", color="#2874A6")
        ax.bar([i + width/2 for i in x], recalls, width, label=f"Rappel@{TOP_K}", color="#1E8449")
        ax.set_xticks(list(x))
        ax.set_xticklabels(methods)
        ax.set_ylim(0, 1.05)
        ax.set_ylabel("Score")
        ax.set_title(f"Precision et rappel par methode (top-{TOP_K})")
        ax.legend()
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "benchmark_precision_recall.png", dpi=200)
        plt.close()

        # Response time chart
        fig, ax = plt.subplots(figsize=(7, 4.5))
        ax.bar(methods, times_ms, color="#B9770E")
        ax.set_ylabel("Temps de reponse moyen (ms)")
        ax.set_title("Temps de reponse moyen par methode")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "benchmark_temps_reponse.png", dpi=200)
        plt.close()

        print(" Graphiques sauvegardes -> benchmark_precision_recall.png, benchmark_temps_reponse.png")
    except ImportError:
        print("matplotlib non installe : graphiques non generes "
              "(pip install matplotlib --break-system-packages).")


if __name__ == "__main__":
    main()
