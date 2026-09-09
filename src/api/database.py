"""
Persistance GED compatible SQLite en developpement et PostgreSQL en production.

Le backend utilise SQLite par defaut pour rester executable sur un poste local.
En entreprise, il suffit de definir GED_DATABASE_URL avec une URL PostgreSQL :
postgresql://user:password@host:5432/ged
"""

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any


def database_url(metadata_path: str = "data/metadata/document_metadata.json") -> str:
    return os.getenv("GED_DATABASE_URL") or f"sqlite:///{Path(metadata_path).with_suffix('.db')}"


def is_postgres(url: str) -> bool:
    return url.startswith("postgresql://") or url.startswith("postgres://")


@contextmanager
def connect(metadata_path: str = "data/metadata/document_metadata.json"):
    url = database_url(metadata_path)
    if is_postgres(url):
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:
            raise RuntimeError(
                "Le mode PostgreSQL necessite psycopg. Installe : pip install psycopg[binary]"
            ) from exc

        connection = psycopg.connect(url, row_factory=dict_row)
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()
        return

    path = Path(url.replace("sqlite:///", "", 1))
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def placeholder(metadata_path: str = "data/metadata/document_metadata.json") -> str:
    return "%s" if is_postgres(database_url(metadata_path)) else "?"


def execute(connection, query: str, params: tuple = ()):
    cursor = connection.cursor()
    cursor.execute(query, params)
    return cursor


def rows_to_dicts(rows) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def init_db(metadata_path: str = "data/metadata/document_metadata.json") -> None:
    url = database_url(metadata_path)
    with connect(metadata_path) as connection:
        if is_postgres(url):
            statements = postgres_schema()
        else:
            statements = sqlite_schema()
        for statement in statements:
            execute(connection, statement)


def sqlite_schema() -> list[str]:
    return [
        """
        CREATE TABLE IF NOT EXISTS document_metadata (
            filename TEXT PRIMARY KEY,
            category TEXT NOT NULL DEFAULT 'Non classe',
            author TEXT NOT NULL DEFAULT '',
            description TEXT NOT NULL DEFAULT '',
            tags TEXT NOT NULL DEFAULT '[]',
            status TEXT NOT NULL DEFAULT 'Indexe',
            folder TEXT NOT NULL DEFAULT '/',
            allowed_roles TEXT NOT NULL DEFAULT '[]',
            updated_at TEXT,
            deleted INTEGER NOT NULL DEFAULT 0,
            deleted_at TEXT,
            deleted_by TEXT NOT NULL DEFAULT ''
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS workflow_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            from_status TEXT NOT NULL,
            to_status TEXT NOT NULL,
            comment TEXT NOT NULL DEFAULT '',
            actor TEXT NOT NULL DEFAULT 'Utilisateur demo',
            created_at TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS document_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            version INTEGER NOT NULL,
            checksum TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            size_label TEXT NOT NULL,
            created_at TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'upload',
            UNIQUE(filename, checksum)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL,
            permissions TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1
        )
        """,
    ]


def postgres_schema() -> list[str]:
    return [
        """
        CREATE TABLE IF NOT EXISTS document_metadata (
            filename TEXT PRIMARY KEY,
            category TEXT NOT NULL DEFAULT 'Non classe',
            author TEXT NOT NULL DEFAULT '',
            description TEXT NOT NULL DEFAULT '',
            tags JSONB NOT NULL DEFAULT '[]'::jsonb,
            status TEXT NOT NULL DEFAULT 'Indexe',
            folder TEXT NOT NULL DEFAULT '/',
            allowed_roles JSONB NOT NULL DEFAULT '[]'::jsonb,
            updated_at TEXT,
            deleted BOOLEAN NOT NULL DEFAULT FALSE,
            deleted_at TEXT,
            deleted_by TEXT NOT NULL DEFAULT ''
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS workflow_actions (
            id BIGSERIAL PRIMARY KEY,
            filename TEXT NOT NULL,
            from_status TEXT NOT NULL,
            to_status TEXT NOT NULL,
            comment TEXT NOT NULL DEFAULT '',
            actor TEXT NOT NULL DEFAULT 'Utilisateur demo',
            created_at TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS document_versions (
            id BIGSERIAL PRIMARY KEY,
            filename TEXT NOT NULL,
            version INTEGER NOT NULL,
            checksum TEXT NOT NULL,
            size_bytes BIGINT NOT NULL,
            size_label TEXT NOT NULL,
            created_at TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'upload',
            UNIQUE(filename, checksum)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL,
            permissions JSONB NOT NULL,
            password_hash TEXT NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE
        )
        """,
    ]


def encode_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def decode_json(value: Any, fallback):
    if value is None:
        return fallback
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return fallback
