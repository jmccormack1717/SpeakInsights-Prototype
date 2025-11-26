"""Simple user authentication and JWT utilities."""
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Dict, Any
import hashlib
import hmac
import secrets

import jwt

from app.config import settings


USERS_DB_PATH = Path(settings.database_path) / "auth.db"


def _get_connection() -> sqlite3.Connection:
    """Get a SQLite connection to the users database."""
    USERS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(USERS_DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def _hash_password(password: str, salt: Optional[str] = None) -> str:
    """
    Hash a password with a salt using SHA-256.

    Stored format: salt$hash
    This is sufficient for a demo project; for production use, prefer bcrypt/argon2.
    """
    if salt is None:
        salt = secrets.token_hex(16)
    pwd_bytes = password.encode("utf-8")
    salt_bytes = salt.encode("utf-8")
    digest = hashlib.sha256(salt_bytes + pwd_bytes).hexdigest()
    return f"{salt}${digest}"


def _verify_password(password: str, stored: str) -> bool:
    """Verify a password against a stored salt$hash value."""
    try:
        salt, _hash = stored.split("$", 1)
    except ValueError:
        return False
    candidate = _hash_password(password, salt)
    # Use constant-time comparison
    return hmac.compare_digest(candidate, stored)


def create_user(email: str, password: str, full_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new user. Raises sqlite3.IntegrityError if email already exists.

    Returns a simple user dict with an application-level user_id (string).
    """
    conn = _get_connection()
    try:
        password_hash = _hash_password(password)
        created_at = datetime.now(timezone.utc).isoformat()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO users (email, full_name, password_hash, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (email.lower().strip(), full_name, password_hash, created_at),
        )
        user_pk = cur.lastrowid
        conn.commit()
    finally:
        conn.close()

    user_id = str(user_pk)
    return {
        "user_id": user_id,
        "email": email.lower().strip(),
        "full_name": full_name,
    }


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Fetch a user record by email."""
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, email, full_name, password_hash, created_at FROM users WHERE email = ?",
            (email.lower().strip(),),
        )
        row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        return None

    return {
        "user_id": str(row[0]),
        "email": row[1],
        "full_name": row[2],
        "password_hash": row[3],
        "created_at": row[4],
    }


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Validate credentials and return a user dict if correct, else None."""
    user = get_user_by_email(email)
    if not user:
        return None
    if not _verify_password(password, user["password_hash"]):
        return None
    # Don't leak hash
    user.pop("password_hash", None)
    return user


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token."""
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )
    return payload


