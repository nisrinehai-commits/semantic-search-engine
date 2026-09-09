from fastapi import APIRouter, Request

from src.api.schemas import SearchRequest

router = APIRouter()


@router.get("/")
def root():
    from src.api.main import root as root_fn

    return root_fn()


@router.get("/health")
def health():
    from src.api.main import health as health_fn

    return health_fn()


@router.get("/stats")
def stats():
    from src.api.main import stats as stats_fn

    return stats_fn()


@router.get("/dashboard")
def dashboard(request: Request):
    from src.api.main import dashboard as dashboard_fn, optional_current_user

    authorization = request.headers.get("authorization")
    current_user = optional_current_user(authorization)
    return dashboard_fn(current_user=current_user)


@router.post("/search")
def search_documents(request: SearchRequest):
    from src.api.main import search_documents as search_documents_fn

    return search_documents_fn(request)
