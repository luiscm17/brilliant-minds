"""Chats router used by the frontend chat flow."""

import os

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.agents.adaptation_agent import run_adaptation_pipeline
from src.agents.comprehension_agent import comprehension_agent
from src.agents.concept_agent import concept_agent
from src.core.dependencies import get_current_user_id
from src.models.schemas import (
    ChatMessage,
    ChatResponse,
    CreateChatResponse,
    ShareResponse,
)
from src.services import cosmos_service, search_service


class ComprehensionRequest(BaseModel):
    simplified_text: str


class ChatTitleUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=100)


class SimpleTextRequest(BaseModel):
    simplified_text: str


router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("", response_model=list[dict])
async def list_chats(user_id: str = Depends(get_current_user_id)):
    chats = await cosmos_service.list_user_chats(user_id)
    return [
        {
            "chatId": c["id"],
            "title": c.get("title", "Chat"),
            "userId": c["user_id"],
            "createdAt": c["created_at"],
        }
        for c in chats
    ]


@router.post("", response_model=CreateChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(body: dict, user_id: str = Depends(get_current_user_id)):
    chat = await cosmos_service.create_chat(user_id, body.get("title"))
    return CreateChatResponse(chatId=chat["id"])


@router.patch("/{chat_id}", response_model=dict)
async def update_chat_title(
    chat_id: str,
    body: ChatTitleUpdate,
    user_id: str = Depends(get_current_user_id),
):
    updated = await cosmos_service.update_chat_title(chat_id, user_id, body.title)
    if not updated:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {
        "chatId": updated["id"],
        "title": updated["title"],
        "userId": updated["user_id"],
        "createdAt": updated["created_at"],
    }


@router.post("/{chat_id}/messages", response_model=ChatResponse)
async def send_message(
    chat_id: str,
    body: ChatMessage,
    user_id: str = Depends(get_current_user_id),
):
    profile = await cosmos_service.get_user_profile(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    rag_chunks: list[str] = []
    try:
        if body.document_ids:
            rag_chunks = await search_service.search_context(
                body.message,
                user_id,
                top_k=max(3, len(body.document_ids)),
                document_ids=body.document_ids,
            )
        else:
            rag_chunks = await search_service.search_context(body.message, user_id, top_k=5)
    except Exception:
        rag_chunks = []

    response = await run_adaptation_pipeline(
        message=body.message,
        profile=profile,
        rag_chunks=rag_chunks,
        fatigue_level=body.fatigue_level,
        target_language=body.target_language,
    )
    await cosmos_service.save_progress(
        user_id,
        response.reading_level_used or profile.reading_level,
        profile.preset,
    )
    return response


@router.post("/{chat_id}/share", response_model=ShareResponse)
async def share_result(
    chat_id: str,
    body: ChatResponse,
    user_id: str = Depends(get_current_user_id),
):
    token = await cosmos_service.create_share(user_id, body.model_dump(by_alias=True))
    base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    return ShareResponse(shareToken=token, shareUrl=f"{base_url}/shared/{token}")


@router.delete("/{chat_id}", status_code=204)
async def delete_chat(chat_id: str, user_id: str = Depends(get_current_user_id)):
    deleted = await cosmos_service.delete_chat(chat_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Chat not found")


@router.post("/{chat_id}/comprehension")
async def get_comprehension(
    chat_id: str,
    body: ComprehensionRequest,
    user_id: str = Depends(get_current_user_id),
):
    agent = await comprehension_agent()
    questions = await agent.run(body.simplified_text)
    return {"questions": questions}


@router.post("/{chat_id}/concept-map")
async def get_concept_map(
    chat_id: str,
    body: SimpleTextRequest,
    user_id: str = Depends(get_current_user_id),
):
    agent = await concept_agent()
    return await agent.run(body.simplified_text)
