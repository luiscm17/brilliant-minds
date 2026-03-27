import asyncio
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from src.config.settings import AuthStorageSettings
from src.core.exceptions import EmailAlreadyExistsError, InvalidCredentialsError
from src.core.security import create_access_token, hash_password, verify_password
from src.models.schemas.auth import AuthUser, AuthResponse, UserCreate, UserLogin


DB_PATH = AuthStorageSettings.get_db_path()
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


with _get_connection() as conn:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )"""
    )


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _build_auth_response(user_id: str, email: str, name: str) -> AuthResponse:
    token = create_access_token(user_id)
    return AuthResponse(
        token=token,
        userId=user_id,
        user=AuthUser(userId=user_id, email=email, name=name),
    )


def _insert_user(
    user_id: str, email: str, name: str, password: str, created_at: str
) -> None:
    with _get_connection() as conn:
        conn.execute(
            "INSERT INTO users (id, email, name, password, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, email, name, password, created_at),
        )


def _fetch_user_by_email(email: str) -> sqlite3.Row | None:
    with _get_connection() as conn:
        cursor = conn.execute(
            "SELECT id, email, name, password FROM users WHERE email = ?", (email,)
        )
        return cursor.fetchone()


async def register_user(body: UserCreate) -> AuthResponse:
    """Register a new user backed by a lightweight sqlite store."""
    normalized_email = _normalize_email(body.email)
    user_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    hashed_password = hash_password(body.password)

    try:
        await asyncio.to_thread(
            _insert_user,
            user_id,
            normalized_email,
            body.name.strip(),
            hashed_password,
            created_at,
        )
    except sqlite3.IntegrityError as exc:
        raise EmailAlreadyExistsError() from exc

    return _build_auth_response(user_id, normalized_email, body.name.strip())


async def login_user(body: UserLogin) -> AuthResponse:
    """Authenticate with email + password and return tokens."""
    normalized_email = _normalize_email(body.email)
    user_row = await asyncio.to_thread(_fetch_user_by_email, normalized_email)

    if not user_row or not verify_password(body.password, user_row["password"]):
        raise InvalidCredentialsError()

    return _build_auth_response(user_row["id"], normalized_email, user_row["name"])
