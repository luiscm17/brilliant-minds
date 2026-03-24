"""Auth router for register/login endpoints used by the frontend."""

import uuid

from fastapi import APIRouter, HTTPException, status

from src.core.security import create_access_token, hash_password, verify_password
from src.models.schemas import AuthResponse, AuthUser, UserCreate, UserLogin
from src.services import cosmos_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserCreate):
    existing = await cosmos_service.get_user_by_email(body.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user_id = str(uuid.uuid4())
    hashed = hash_password(body.password)
    await cosmos_service.create_user_profile(user_id, body.email, body.name, hashed)
    token = create_access_token(user_id)
    return AuthResponse(
        token=token,
        userId=user_id,
        user=AuthUser(userId=user_id, email=body.email, name=body.name),
    )


@router.post("/login", response_model=AuthResponse)
async def login(body: UserLogin):
    user = await cosmos_service.get_user_by_email(body.email)
    if not user or not verify_password(body.password, user.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    user_id = user["user_id"]
    token = create_access_token(user_id)
    return AuthResponse(
        token=token,
        userId=user_id,
        user=AuthUser(userId=user_id, email=user["email"], name=user["name"]),
    )
