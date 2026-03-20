"""Chats router — create conversations and send messages to the AAM agent."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.core.dependencies import get_current_user_id
from src.models.schemas import ChatCreate, ChatResponse, ChatMessage, SimplifiedResponse
from src.services import cosmos_service, search_service
from src.agents.adaptation_agent import run_adaptation_pipeline

router = APIRouter(prefix="/chats", tags=["chats"])


@router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(body: ChatCreate, user_id: str = Depends(get_current_user_id)):
    chat = await cosmos_service.create_chat(user_id, body.title)
    return ChatResponse(
        chat_id=chat["id"],
        title=chat["title"],
        user_id=chat["user_id"],
        created_at=chat["created_at"],
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

    # 2. Retrieve RAG context from referenced documents
    rag_chunks: list[str] = []
    if body.document_ids:
        for _ in body.document_ids:
            chunks = await search_service.search_context(body.message, user_id, top_k=3)
            rag_chunks.extend(chunks)
    else:
        # Search across all user documents
        rag_chunks = await search_service.search_context(body.message, user_id, top_k=5)

    # 3. Run the full adaptation pipeline
    response = await run_adaptation_pipeline(
        message=body.message,
        profile=profile,
        rag_chunks=rag_chunks,
    )

    return response
