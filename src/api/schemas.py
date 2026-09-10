"""
Schemas de donnees pour l'API de recherche semantique.
"""

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Corps de la requete POST /search."""

    query: str = Field(..., min_length=1, description="Texte de la requete utilisateur")
    top_k: int = Field(default=3, ge=1, le=20, description="Nombre de resultats a retourner")
    mode: str = Field(default="hybrid", description="Mode : semantic, keyword ou hybrid")
    semantic_weight: float = Field(default=0.35, ge=0, le=1, description="Poids du score semantique")
    keyword_weight: float = Field(default=0.65, ge=0, le=1, description="Poids du score mots-cles")


class SearchResult(BaseModel):
    """Un resultat individuel de recherche."""

    filename: str
    source_type: str = "unknown"
    chunk_id: int = 0
    start_char: int = 0
    end_char: int = 0
    score: float
    semantic_score: float = 0.0
    keyword_score: float = 0.0
    search_mode: str = "hybrid"
    text_preview: str


class SearchResponse(BaseModel):
    """Corps de la reponse de POST /search."""

    query: str
    results: list[SearchResult]


class DocumentItem(BaseModel):
    """Document affiche dans la bibliotheque GED."""

    name: str
    title: str
    extension: str
    type: str
    size_bytes: int
    size_label: str
    added_at: str
    modified_at: str
    page_count: int | None = None
    status: str = "Indexe"
    processed: bool = False
    category: str = "Non classe"
    author: str = ""
    description: str = ""
    tags: list[str] = []
    folder: str = "/"
    allowed_roles: list[str] = []
    deleted: bool = False
    deleted_at: str | None = None
    download_url: str
    preview_url: str


class DocumentListResponse(BaseModel):
    """Reponse paginee de la bibliotheque documentaire."""

    items: list[DocumentItem]
    total: int
    page: int
    per_page: int
    pages: int


class DocumentPreviewResponse(BaseModel):
    """Contenu de previsualisation textuelle d'un document."""

    name: str
    type: str
    mode: str
    content: str


class DocumentMetadata(BaseModel):
    """Metadonnees GED modifiables par l'utilisateur."""

    category: str = Field(default="Non classe", max_length=80)
    author: str = Field(default="", max_length=120)
    description: str = Field(default="", max_length=1000)
    tags: list[str] = Field(default_factory=list)
    status: str = Field(default="Indexe", max_length=40)
    folder: str = Field(default="/", max_length=160)
    allowed_roles: list[str] = Field(default_factory=list)


class DocumentMetadataResponse(DocumentMetadata):
    """Metadonnees rattachees a un document."""

    filename: str
    updated_at: str | None = None


class WorkflowTransitionRequest(BaseModel):
    """Demande de changement d'etat documentaire."""

    status: str = Field(..., max_length=40)
    comment: str = Field(default="", max_length=1000)
    actor: str = Field(default="Utilisateur demo", max_length=120)


class WorkflowActionItem(BaseModel):
    """Action historisee dans le workflow documentaire."""

    filename: str
    from_status: str
    to_status: str
    comment: str = ""
    actor: str = "Utilisateur demo"
    created_at: str


class WorkflowHistoryResponse(BaseModel):
    """Historique de workflow d'un document."""

    filename: str
    current_status: str
    steps: list[str]
    actions: list[WorkflowActionItem]


class DashboardBucket(BaseModel):
    """Valeur agregee pour un graphique du dashboard."""

    label: str
    count: int


class DashboardRecentDocument(BaseModel):
    """Document recent affiche dans le dashboard."""

    name: str
    title: str
    type: str
    category: str
    status: str
    modified_at: str


class DashboardResponse(BaseModel):
    """Indicateurs GED globaux."""

    total_documents: int
    total_size_bytes: int
    total_size_label: str
    indexed_documents: int
    pending_documents: int
    by_type: list[DashboardBucket]
    by_category: list[DashboardBucket]
    by_status: list[DashboardBucket]
    recent_documents: list[DashboardRecentDocument]
    recent_activity: list[WorkflowActionItem]


class DocumentVersionItem(BaseModel):
    """Version historisee d'un document."""

    filename: str
    version: int
    checksum: str
    size_bytes: int
    size_label: str
    created_at: str
    source: str = "upload"


class DocumentVersionsResponse(BaseModel):
    """Liste des versions connues pour un document."""

    filename: str
    versions: list[DocumentVersionItem]


class SimilarDocumentItem(BaseModel):
    """Document proche ou doublon potentiel."""

    filename: str
    title: str
    type: str
    similarity: float
    reason: str


class SimilarDocumentsResponse(BaseModel):
    """Documents similaires a un document donne."""

    filename: str
    items: list[SimilarDocumentItem]


class DocumentAIAnalysisResponse(BaseModel):
    """Analyse IA locale et explicable d'un document."""

    filename: str
    summary: str
    keywords: list[str]
    suggested_category: str
    confidentiality: str
    similar_documents: list[SimilarDocumentItem]


class AssistantQuestionRequest(BaseModel):
    """Question posee a l'assistant documentaire."""

    question: str = Field(..., min_length=3, description="Question en langage naturel")
    top_k: int = Field(default=5, ge=1, le=10)


class AssistantSourceItem(BaseModel):
    """Source citee par l'assistant documentaire."""

    filename: str
    chunk_id: int
    score: float
    text_preview: str


class AssistantAnswerResponse(BaseModel):
    """Reponse extractive de l'assistant documentaire."""

    question: str
    answer: str
    confidence: float
    sources: list[AssistantSourceItem]


class UserItem(BaseModel):
    """Utilisateur de demonstration pour presenter roles et permissions."""

    id: str
    name: str
    email: str
    role: str
    permissions: list[str]


class LoginRequest(BaseModel):
    """Connexion demo sans mot de passe reel."""

    email: str = Field(..., min_length=3)
    password: str = Field(default="demo123", min_length=3)


class LoginResponse(BaseModel):
    """Session demo retournee par l'API."""

    token: str
    user: UserItem
