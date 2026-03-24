"""Users router for reading and updating the accessibility profile."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.core.dependencies import get_current_user_id
from src.models.schemas import UserProfile, UserProfileUpdate
from src.services import cosmos_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfile | None)
async def get_me(user_id: str = Depends(get_current_user_id)):
    return await cosmos_service.get_user_profile(user_id)


@router.patch("/me", response_model=UserProfile)
async def update_me(
    body: UserProfileUpdate,
    user_id: str = Depends(get_current_user_id),
):
    updated = await cosmos_service.update_user_profile(user_id, body)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return updated
