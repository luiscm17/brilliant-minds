from fastapi import APIRouter, status

from src.models.schemas.auth import AuthResponse, UserCreate, UserLogin
from src.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED, response_model_by_alias=True)
async def register(body: UserCreate):
    """Delegate registration to auth_service."""
    return await auth_service.register_user(body)


@router.post("/login", response_model=AuthResponse, response_model_by_alias=True)
async def login(body: UserLogin):
    """Delegate login to auth_service."""
    return await auth_service.login_user(body)
