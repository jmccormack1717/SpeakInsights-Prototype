"""Auth API routes: simple email/password signup and login."""
from pathlib import Path
import shutil

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from app.core import auth as auth_core
from app.core.database import db_manager


router = APIRouter()


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: EmailStr
    full_name: str | None = None


@router.post("/auth/signup", response_model=AuthResponse)
async def signup(payload: SignupRequest):
    """
    Create a new user account.

    For convenience in this demo, we also seed the user with a copy of the
    built-in MVP dataset if it exists, so new users can query immediately.
    """
    try:
        user = auth_core.create_user(
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
        )
    except Exception as e:
        # Most likely a uniqueness violation on email
        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists.",
        ) from e

    user_id = user["user_id"]

    # Best-effort copy of default MVP dataset for this new user
    try:
        src_db = db_manager.get_database_path("default_user", "mvp_dataset")
        dst_db = db_manager.get_database_path(user_id, "mvp_dataset")
        if src_db.exists() and not dst_db.exists():
            dst_db.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_db, dst_db)
    except Exception:
        # Non-fatal for signup; just log at API layer if needed later
        pass

    token = auth_core.create_access_token({"sub": user_id, "email": user["email"]})
    return AuthResponse(
        access_token=token,
        user_id=user_id,
        email=user["email"],
        full_name=user.get("full_name"),
    )


@router.post("/auth/login", response_model=AuthResponse)
async def login(payload: LoginRequest):
    """Log in an existing user and return an access token."""
    user = auth_core.authenticate_user(email=payload.email, password=payload.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    token = auth_core.create_access_token({"sub": user["user_id"], "email": user["email"]})
    return AuthResponse(
        access_token=token,
        user_id=user["user_id"],
        email=user["email"],
        full_name=user.get("full_name"),
    )


