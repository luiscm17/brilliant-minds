"""Chats router — create conversations and send messages to the AAM agent."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.core.dependencies import get_current_user_id
from src.models.schemas import ChatCreate, ChatResponse, ChatMessage, SimplifiedResponse, ShareResponse
from src.services import cosmos_service
from src.agents.adaptation_agent import run_adaptation_pipeline
from src.agents.comprehension_agent import comprehension_agent
from src.agents.concept_agent import concept_agent
from pydantic import BaseModel, Field
import os

class ComprehensionRequest(BaseModel):
    simplified_text: str

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("", response_model=list[ChatResponse])
async def list_chats(user_id: str = Depends(get_current_user_id)):
    chats = await cosmos_service.list_user_chats(user_id)
    return [
        ChatResponse(
            chat_id=c["id"],
            title=c.get("title", "Chat"),
            user_id=c["user_id"],
            created_at=c["created_at"],
        )
        for c in chats
    ]


@router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(body: ChatCreate, user_id: str = Depends(get_current_user_id)):
    chat = await cosmos_service.create_chat(user_id, body.title)
    return ChatResponse(
        chat_id=chat["id"],
        title=chat["title"],
        user_id=chat["user_id"],
        created_at=chat["created_at"],
    )


class ChatTitleUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=100)


@router.patch("/{chat_id}", response_model=ChatResponse)
async def update_chat_title(
    chat_id: str,
    body: ChatTitleUpdate,
    user_id: str = Depends(get_current_user_id),
):
    updated = await cosmos_service.update_chat_title(chat_id, user_id, body.title)
    if not updated:
        raise HTTPException(status_code=404, detail="Chat not found")
    return ChatResponse(
        chat_id=updated["id"],
        title=updated["title"],
        user_id=updated["user_id"],
        created_at=updated["created_at"],
    )


@router.post("/{chat_id}/messages", response_model=SimplifiedResponse)
async def send_message(
    chat_id: str,
    body: ChatMessage,
    user_id: str = Depends(get_current_user_id),
):
    # 1. Retrieve user profile
    profile = await cosmos_service.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found")

    # 2. Run the full Agentic RAG + adaptation pipeline
    # The AgenticRAGAgent decides autonomously when and what to search
    response = await run_adaptation_pipeline(
        message=body.message,
        profile=profile,
        user_id=user_id,
        fatigue_level=body.fatigue_level,
        target_language=body.target_language,
    )

    # Save progress for history chart
    await cosmos_service.save_progress(user_id, response.reading_level_used or profile.reading_level, profile.preset)

    return response


@router.post("/{chat_id}/share", response_model=ShareResponse)
async def share_result(
    chat_id: str,
    body: SimplifiedResponse,
    user_id: str = Depends(get_current_user_id),
):
    token = await cosmos_service.create_share(user_id, body.model_dump())
    base_url = os.getenv("FRONTEND_URL", "http://localhost:5174")
    return ShareResponse(share_token=token, share_url=f"{base_url}/shared/{token}")


@router.post("/{chat_id}/concept-map")
async def get_concept_map(
    chat_id: str,
    body: ComprehensionRequest,
    user_id: str = Depends(get_current_user_id),
):
    agent = await concept_agent()
    result = await agent.run(body.simplified_text)
    return result


@router.delete("/{chat_id}", status_code=204)
async def delete_chat(
    chat_id: str,
    user_id: str = Depends(get_current_user_id),
):
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
