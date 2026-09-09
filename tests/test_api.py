"""
Tests unitaires pour l'API REST.
"""

from fastapi.testclient import TestClient

import src.api.main as api_main
from src.api.main import app

client = TestClient(app)


def admin_headers():
    api_main.seed_default_users()
    token = api_main.create_jwt(api_main.default_users()[0])
    return {"Authorization": f"Bearer {token}"}


def role_headers(role):
    api_main.seed_default_users()
    user = next(user for user in api_main.default_users() if user["role"] == role)
    token = api_main.create_jwt(user)
    return {"Authorization": f"Bearer {token}"}


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_stats_endpoint():
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["documents"] > 0
    assert data["chunks"] > 0


def test_search_endpoint_returns_results():
    response = client.post(
        "/search",
        json={"query": "recherche sur les ressources de peche", "top_k": 3},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 3
    assert "chunk_id" in data["results"][0]
    assert "semantic_score" in data["results"][0]
    assert "keyword_score" in data["results"][0]


def test_search_endpoint_default_top_k():
    response = client.post(
        "/search",
        json={"query": "recherche sur les ressources de peche"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 3


def test_search_endpoint_rejects_empty_query():
    response = client.post("/search", json={"query": "", "top_k": 3})
    assert response.status_code == 422


def test_search_endpoint_rejects_invalid_top_k():
    response = client.post("/search", json={"query": "test", "top_k": 100})
    assert response.status_code == 422


def test_search_endpoint_accepts_hybrid_parameters():
    response = client.post(
        "/search",
        json={
            "query": "aquaculture marine",
            "top_k": 2,
            "mode": "hybrid",
            "semantic_weight": 0.6,
            "keyword_weight": 0.4,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 2
    assert data["results"][0]["search_mode"] == "hybrid"


def test_upload_endpoint_indexes_txt(monkeypatch, tmp_path):
    monkeypatch.setattr(api_main, "RAW_DIR", str(tmp_path / "raw"))
    monkeypatch.setattr(api_main, "PROCESSED_DIR", str(tmp_path / "processed"))
    monkeypatch.setattr(api_main, "EMBEDDINGS_DIR", str(tmp_path / "embeddings"))
    monkeypatch.setattr(api_main, "METADATA_PATH", str(tmp_path / "metadata.json"))
    monkeypatch.setattr(api_main, "WORKFLOW_LOG_PATH", str(tmp_path / "workflow.json"))
    monkeypatch.setattr(api_main, "VERSIONS_PATH", str(tmp_path / "versions.json"))
    monkeypatch.setattr(
        api_main,
        "rebuild_index",
        lambda: (tmp_path / "embeddings").mkdir(parents=True, exist_ok=True),
    )
    monkeypatch.setattr(
        api_main,
        "stats",
        lambda: {"documents": 1, "chunks": 1, "dimension": 384, "index_type": "test"},
    )

    response = client.post(
        "/upload?filename=note.txt",
        content=b"Document texte ajoute depuis l interface.",
        headers={"content-type": "application/octet-stream", **admin_headers()},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "indexed"
    assert data["filename"] == "note.txt"
    assert (tmp_path / "processed" / "note_txt.txt").exists()


def test_documents_endpoint_lists_files(monkeypatch, tmp_path):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()
    (raw_dir / "rapport.txt").write_text("contenu", encoding="utf-8")
    (processed_dir / "rapport_txt.txt").write_text("contenu", encoding="utf-8")

    monkeypatch.setattr(api_main, "RAW_DIR", str(raw_dir))
    monkeypatch.setattr(api_main, "PROCESSED_DIR", str(processed_dir))

    response = client.get("/documents")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "rapport.txt"
    assert data["items"][0]["processed"] is True


def test_documents_endpoint_filters_by_type(monkeypatch, tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "rapport.txt").write_text("contenu", encoding="utf-8")
    (raw_dir / "note.pdf").write_bytes(b"%PDF-1.4")

    monkeypatch.setattr(api_main, "RAW_DIR", str(raw_dir))
    monkeypatch.setattr(api_main, "PROCESSED_DIR", str(tmp_path / "processed"))

    response = client.get("/documents?file_type=TXT")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["type"] == "TXT"


def test_preview_txt_document(monkeypatch, tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "rapport.txt").write_text("Apercu documentaire", encoding="utf-8")

    monkeypatch.setattr(api_main, "RAW_DIR", str(raw_dir))

    response = client.get("/documents/rapport.txt/preview")

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "text"
    assert "Apercu documentaire" in data["content"]


def test_download_document(monkeypatch, tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "rapport.txt").write_text("Telechargement", encoding="utf-8")

    monkeypatch.setattr(api_main, "RAW_DIR", str(raw_dir))

    response = client.get("/documents/rapport.txt/download")

    assert response.status_code == 200
    assert response.text == "Telechargement"


def test_update_document_metadata(monkeypatch, tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "rapport.txt").write_text("Metadonnees", encoding="utf-8")

    monkeypatch.setattr(api_main, "RAW_DIR", str(raw_dir))
    monkeypatch.setattr(api_main, "METADATA_PATH", str(tmp_path / "metadata.json"))

    response = client.put(
        "/documents/rapport.txt/metadata",
        json={
            "category": "Recherche",
            "author": "INRH",
            "description": "Rapport documentaire",
            "tags": ["peche", "rapport", "peche"],
            "status": "Valide",
        },
        headers=admin_headers(),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "Recherche"
    assert data["author"] == "INRH"
    assert data["tags"] == ["peche", "rapport"]
    assert data["status"] == "Valide"


def test_documents_endpoint_searches_metadata(monkeypatch, tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "rapport.txt").write_text("contenu", encoding="utf-8")

    monkeypatch.setattr(api_main, "RAW_DIR", str(raw_dir))
    monkeypatch.setattr(api_main, "PROCESSED_DIR", str(tmp_path / "processed"))
    monkeypatch.setattr(api_main, "METADATA_PATH", str(tmp_path / "metadata.json"))

    client.put(
        "/documents/rapport.txt/metadata",
        json={
            "category": "Aquaculture",
            "author": "Equipe scientifique",
            "description": "Document sur la production marine",
            "tags": ["innovation"],
            "status": "Indexe",
        },
        headers=admin_headers(),
    )

    response = client.get("/documents?q=production")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["category"] == "Aquaculture"


def test_documents_endpoint_filters_by_category(monkeypatch, tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "a.txt").write_text("a", encoding="utf-8")
    (raw_dir / "b.txt").write_text("b", encoding="utf-8")

    monkeypatch.setattr(api_main, "RAW_DIR", str(raw_dir))
    monkeypatch.setattr(api_main, "PROCESSED_DIR", str(tmp_path / "processed"))
    monkeypatch.setattr(api_main, "METADATA_PATH", str(tmp_path / "metadata.json"))

    client.put("/documents/a.txt/metadata", json={"category": "RH", "tags": [], "status": "Indexe"}, headers=admin_headers())
    client.put("/documents/b.txt/metadata", json={"category": "Finance", "tags": [], "status": "Indexe"}, headers=admin_headers())

    response = client.get("/documents?category=RH")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "a.txt"


def test_workflow_transition_updates_status_and_history(monkeypatch, tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "rapport.txt").write_text("workflow", encoding="utf-8")

    monkeypatch.setattr(api_main, "RAW_DIR", str(raw_dir))
    monkeypatch.setattr(api_main, "METADATA_PATH", str(tmp_path / "metadata.json"))
    monkeypatch.setattr(api_main, "WORKFLOW_LOG_PATH", str(tmp_path / "workflow.json"))

    response = client.post(
        "/documents/rapport.txt/workflow",
        json={
            "status": "Soumis",
            "comment": "Document pret pour validation",
            "actor": "Employe demo",
        },
        headers=admin_headers(),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["current_status"] == "Soumis"
    assert len(data["actions"]) == 1
    assert data["actions"][0]["to_status"] == "Soumis"
    assert data["actions"][0]["comment"] == "Document pret pour validation"

    metadata_response = client.get("/documents/rapport.txt/metadata")
    assert metadata_response.json()["status"] == "Soumis"


def test_workflow_rejects_invalid_status(monkeypatch, tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "rapport.txt").write_text("workflow", encoding="utf-8")

    monkeypatch.setattr(api_main, "RAW_DIR", str(raw_dir))
    monkeypatch.setattr(api_main, "METADATA_PATH", str(tmp_path / "metadata.json"))
    monkeypatch.setattr(api_main, "WORKFLOW_LOG_PATH", str(tmp_path / "workflow.json"))

    response = client.post(
        "/documents/rapport.txt/workflow",
        json={"status": "Etat impossible", "comment": "", "actor": "Test"},
        headers=admin_headers(),
    )

    assert response.status_code == 400


def test_dashboard_returns_document_aggregates(monkeypatch, tmp_path):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()
    (raw_dir / "rapport.txt").write_text("dashboard", encoding="utf-8")
    (raw_dir / "note.docx").write_bytes(b"placeholder")
    (processed_dir / "rapport_txt.txt").write_text("dashboard", encoding="utf-8")

    monkeypatch.setattr(api_main, "RAW_DIR", str(raw_dir))
    monkeypatch.setattr(api_main, "PROCESSED_DIR", str(processed_dir))
    monkeypatch.setattr(api_main, "METADATA_PATH", str(tmp_path / "metadata.json"))
    monkeypatch.setattr(api_main, "WORKFLOW_LOG_PATH", str(tmp_path / "workflow.json"))

    client.put(
        "/documents/rapport.txt/metadata",
        json={"category": "Recherche", "tags": ["test"], "status": "Soumis"},
        headers=admin_headers(),
    )

    response = client.get("/dashboard")

    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] == 2
    assert data["indexed_documents"] == 1
    assert data["pending_documents"] == 1
    assert any(bucket["label"] == "TXT" for bucket in data["by_type"])
    assert any(bucket["label"] == "Recherche" for bucket in data["by_category"])


def test_dashboard_includes_recent_workflow_activity(monkeypatch, tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "rapport.txt").write_text("workflow", encoding="utf-8")

    monkeypatch.setattr(api_main, "RAW_DIR", str(raw_dir))
    monkeypatch.setattr(api_main, "METADATA_PATH", str(tmp_path / "metadata.json"))
    monkeypatch.setattr(api_main, "WORKFLOW_LOG_PATH", str(tmp_path / "workflow.json"))

    client.post(
        "/documents/rapport.txt/workflow",
        json={"status": "Soumis", "comment": "A valider", "actor": "Demo"},
        headers=admin_headers(),
    )

    response = client.get("/dashboard")

    assert response.status_code == 200
    data = response.json()
    assert data["recent_activity"][0]["filename"] == "rapport.txt"
    assert data["recent_activity"][0]["to_status"] == "Soumis"


def test_soft_delete_hides_and_restores_document(monkeypatch, tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "rapport.txt").write_text("corbeille", encoding="utf-8")

    monkeypatch.setattr(api_main, "RAW_DIR", str(raw_dir))
    monkeypatch.setattr(api_main, "PROCESSED_DIR", str(tmp_path / "processed"))
    monkeypatch.setattr(api_main, "METADATA_PATH", str(tmp_path / "metadata.json"))
    monkeypatch.setattr(api_main, "WORKFLOW_LOG_PATH", str(tmp_path / "workflow.json"))

    delete_response = client.delete("/documents/rapport.txt", headers=admin_headers())
    assert delete_response.status_code == 200

    hidden_response = client.get("/documents")
    assert hidden_response.json()["total"] == 0

    deleted_response = client.get("/documents?include_deleted=true")
    assert deleted_response.json()["total"] == 1
    assert deleted_response.json()["items"][0]["deleted"] is True

    restore_response = client.post("/documents/rapport.txt/restore", headers=admin_headers())
    assert restore_response.status_code == 200
    visible_response = client.get("/documents")
    assert visible_response.json()["total"] == 1


def test_document_versions_returns_existing_file_version(monkeypatch, tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "rapport.txt").write_text("version initiale", encoding="utf-8")

    monkeypatch.setattr(api_main, "RAW_DIR", str(raw_dir))
    monkeypatch.setattr(api_main, "VERSIONS_PATH", str(tmp_path / "versions.json"))

    response = client.get("/documents/rapport.txt/versions")

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "rapport.txt"
    assert data["versions"][0]["version"] == 1
    assert len(data["versions"][0]["checksum"]) == 64


def test_ai_analysis_suggests_metadata_and_similar_documents(monkeypatch, tmp_path):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()
    (raw_dir / "peche.txt").write_text("source", encoding="utf-8")
    (raw_dir / "copie.txt").write_text("source", encoding="utf-8")
    text = "La peche durable protege les ressources halieutiques et les ecosystemes marins. " * 4
    (processed_dir / "peche_txt.txt").write_text(text, encoding="utf-8")
    (processed_dir / "copie_txt.txt").write_text(text, encoding="utf-8")

    monkeypatch.setattr(api_main, "RAW_DIR", str(raw_dir))
    monkeypatch.setattr(api_main, "PROCESSED_DIR", str(processed_dir))
    monkeypatch.setattr(api_main, "METADATA_PATH", str(tmp_path / "metadata.json"))

    response = client.get("/documents/peche.txt/ai")

    assert response.status_code == 200
    data = response.json()
    assert data["suggested_category"] == "Peche"
    assert "peche" in data["keywords"]
    assert data["similar_documents"][0]["filename"] == "copie.txt"


def test_similar_documents_detects_potential_duplicate(monkeypatch, tmp_path):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()
    (raw_dir / "a.txt").write_text("a", encoding="utf-8")
    (raw_dir / "b.txt").write_text("b", encoding="utf-8")
    (processed_dir / "a_txt.txt").write_text("aquaculture marine production larves", encoding="utf-8")
    (processed_dir / "b_txt.txt").write_text("aquaculture marine production larves", encoding="utf-8")

    monkeypatch.setattr(api_main, "RAW_DIR", str(raw_dir))
    monkeypatch.setattr(api_main, "PROCESSED_DIR", str(processed_dir))
    monkeypatch.setattr(api_main, "METADATA_PATH", str(tmp_path / "metadata.json"))

    response = client.get("/documents/a.txt/similar")

    assert response.status_code == 200
    data = response.json()
    assert data["items"][0]["reason"] == "Doublon potentiel"


def test_assistant_returns_answer_with_sources(monkeypatch):
    class FakeSearchResponse:
        results = [
            api_main.SearchResult(
                filename="rapport.txt",
                chunk_id=0,
                score=0.91,
                semantic_score=0.9,
                keyword_score=0.8,
                text_preview="La peche durable permet de proteger les ressources halieutiques.",
            )
        ]

    monkeypatch.setattr(api_main, "search_documents", lambda payload: FakeSearchResponse())

    response = client.post("/assistant/ask", json={"question": "Que dit la peche durable ?", "top_k": 1})

    assert response.status_code == 200
    data = response.json()
    assert data["confidence"] == 0.91
    assert data["sources"][0]["filename"] == "rapport.txt"
    assert "rapport.txt" in data["answer"]


def test_users_and_demo_login():
    users_response = client.get("/users", headers=admin_headers())
    assert users_response.status_code == 200
    assert any(user["role"] == "Administrateur" for user in users_response.json())

    login_response = client.post("/auth/login", json={"email": "admin@inrh.demo", "password": "demo123"})
    assert login_response.status_code == 200
    data = login_response.json()
    assert data["user"]["role"] == "Administrateur"
    assert len(data["token"].split(".")) == 3


def test_document_permissions_are_enforced(monkeypatch, tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "confidentiel.txt").write_text("Document reserve validation", encoding="utf-8")

    monkeypatch.setattr(api_main, "RAW_DIR", str(raw_dir))
    monkeypatch.setattr(api_main, "METADATA_PATH", str(tmp_path / "metadata.json"))

    api_main.save_metadata_store(
        {
            "confidentiel.txt": {
                **api_main.default_metadata(),
                "allowed_roles": ["Validateur"],
            }
        }
    )

    denied = client.get("/documents/confidentiel.txt/metadata", headers=role_headers("Employe"))
    allowed = client.get("/documents/confidentiel.txt/metadata", headers=role_headers("Validateur"))

    assert denied.status_code == 403
    assert allowed.status_code == 200
