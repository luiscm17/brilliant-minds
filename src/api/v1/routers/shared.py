"""Public shared results router."""

from fastapi import APIRouter, HTTPException

from src.services import cosmos_service

router = APIRouter(prefix="/shared", tags=["shared"])


@router.get("/{share_token}")
async def get_shared_result(share_token: str):
    data = await cosmos_service.get_share(share_token)
    if not data:
        raise HTTPException(status_code=404, detail="Link no encontrado o expirado")
    return data
