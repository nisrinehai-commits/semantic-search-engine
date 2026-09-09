from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.config import APP_ALLOWED_ORIGINS, METADATA_PATH
from src.api.database import init_db
from src.api.main import migrate_legacy_json_files, seed_default_users


@asynccontextmanager
async def app_lifespan(_: FastAPI):
    init_db(METADATA_PATH)
    migrate_legacy_json_files()
    seed_default_users()
    yield


app = FastAPI(
    title="Prototype de recherche semantique documentaire - INRH",
    description="API de recherche semantique par passages, basee sur SBERT et FAISS.",
    version="1.1.0",
    lifespan=app_lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=APP_ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/app", StaticFiles(directory="static", html=True), name="static")
