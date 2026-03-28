from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.agents.orchestrator_service import orchestrator_service
from src.core.dependencies import get_current_user_id
from src.models.schemas.chats import (
    ChatCreate,
    ChatMessage,
    ChatResponse,
    CreateChatResponse,
    ShareResponse,
)
from src.services import search_service, share_service

router = APIRouter(prefix="/chats", tags=["chats"])
shared_router = APIRouter(prefix="/shared", tags=["shared"])


def _build_simplified_text(
    message: str,
    context_chunks: list[str],
) -> str:
    if not context_chunks:
        return (
            "Resumen guiado:\n"
            f"- Pedido: {message}\n"
            "- Todavia no encontre contexto documental listo.\n"
            "- Puedes seguir conversando mientras termina el indexado."
        )

    context_preview = context_chunks[0].splitlines()[-1].strip()
    return (
        "Resumen guiado:\n"
        f"- Pedido: {message}\n"
        f"- Hallazgo principal: {context_preview[:240]}\n"
        "- La salida esta organizada para lectura mas clara y estable."
    )


def _build_explanation(
    context_chunks: list[str],
    visual_references: list[dict],
) -> str:
    if context_chunks:
        visual_note = (
            f" Tambien se detectaron {len(visual_references)} referencias visuales."
            if visual_references
            else ""
        )
        return (
            f"Se uso grounding con {len(context_chunks)} fragmento(s) recuperados del RAG."
            f"{visual_note}"
        )
    return "El sistema respondio sin grounding porque aun no hay contexto indexado disponible."


@router.post("", response_model=CreateChatResponse, response_model_by_alias=True)
async def create_chat(body: ChatCreate | None = None):
    _ = body
    return CreateChatResponse(chatId=uuid4().hex)


@router.post("/agent", response_model=ChatResponse, response_model_by_alias=True)
async def chat_with_agent(
    body: ChatMessage,
    user_id: str = Depends(get_current_user_id),
):
    """Optional endpoint that sends the prompt directly to the orchestrator."""
    rag_error = None
    try:
        context_chunks, visual_references = await search_service.search_context_bundle(
            body.message,
            user_id=user_id,
            top_k=3,
            document_ids=body.document_ids,
        )
    except Exception as exc:
        context_chunks, visual_references = [], []
        rag_error = str(exc)

    contextual_prompt = body.message
    if context_chunks:
        rag_context = "\n\n".join(
            f"[Contexto {index + 1}]\n{chunk}" for index, chunk in enumerate(context_chunks)
        )
        contextual_prompt = (
            "Responde usando el siguiente contexto documental recuperado por RAG.\n"
            "Si el contexto es suficiente, priorizalo. Si no lo es, dilo con claridad.\n\n"
            f"{rag_context}\n\n"
            f"Pregunta del usuario: {body.message}"
        )

    try:
        agent_text = await orchestrator_service.process_message(
            user_id=user_id,
            user_message=contextual_prompt,
        )

        explanation = _build_explanation(context_chunks, visual_references)
        if rag_error:
            explanation = (
                explanation
                + " El agente respondio, pero el entorno RAG no esta completo: "
                + rag_error
            )

        return ChatResponse(
            originalMessage=body.message,
            simplifiedText=agent_text,
            explanation=explanation,
            tone="empatico",
            searchesPerformed=[body.message] if context_chunks else [],
            visualReferences=visual_references,
            glossary=[],
        )

    except Exception as e:
        print(f"[ERROR] en chat_with_agent: {e}")
        return ChatResponse(
            simplifiedText="Lo siento, ocurrio un error inesperado. Por favor, intentalo de nuevo.",
            explanation="Error en el procesamiento del agente",
            tone="neutral",
            glossary=[],
        )


@router.post(
    "/{chat_id}/messages",
    response_model=ChatResponse,
    response_model_by_alias=True,
)
async def send_message(
    chat_id: str,
    body: ChatMessage,
    user_id: str = Depends(get_current_user_id),
):
    _ = chat_id
    rag_error = None
    try:
        context_chunks, visual_references = await search_service.search_context_bundle(
            body.message,
            user_id=user_id,
            top_k=3,
            document_ids=body.document_ids,
        )
    except Exception as exc:
        context_chunks, visual_references = [], []
        rag_error = str(exc)

    explanation = _build_explanation(context_chunks, visual_references)
    if rag_error:
        explanation = (
            explanation
            + " El backend sigue respondiendo, pero el entorno RAG no esta completo: "
            + rag_error
        )

    return ChatResponse(
        originalMessage=body.message,
        simplifiedText=_build_simplified_text(body.message, context_chunks),
        explanation=explanation,
        tone="calmado" if body.fatigue_level > 0 else "neutral",
        beeLineOverlay=True,
        wcagReport="Draft ready",
        presetUsed="custom",
        readingLevelUsed="A1" if body.fatigue_level > 0 else "A2",
        emojiSummary="documento claro y guiado",
        glossary=[
            {
                "word": "grounding",
                "definition": "usar documentos recuperados como apoyo para responder.",
            }
        ]
        if context_chunks
        else [],
        searchesPerformed=[body.message] if context_chunks else [],
        visualReferences=visual_references,
    )


@router.post("/{chat_id}/comprehension", response_model_by_alias=True)
async def get_comprehension(
    chat_id: str,
    body: dict,
    user_id: str = Depends(get_current_user_id),
):
    _ = (chat_id, body, user_id)
    return {
        "questions": [
            {
                "question": "Cual es la idea principal de la respuesta?",
                "options": {
                    "A": "Que el sistema organiza y explica el contenido.",
                    "B": "Que el documento fue eliminado.",
                    "C": "Que no hay ninguna diferencia visual.",
                },
                "answer": "A",
            }
        ]
    }


@router.post("/{chat_id}/concept-map", response_model_by_alias=True)
async def get_concept_map(
    chat_id: str,
    body: dict,
    user_id: str = Depends(get_current_user_id),
):
    _ = (chat_id, user_id)
    simplified_text = str(body.get("simplified_text", "") or "")
    nodes = [
        {"id": "1", "label": "Consulta"},
        {"id": "2", "label": "RAG"},
        {"id": "3", "label": "Respuesta"},
    ]
    if simplified_text:
        nodes.append({"id": "4", "label": simplified_text[:48]})

    edges = [
        {"source": "1", "target": "2"},
        {"source": "2", "target": "3"},
    ]
    if simplified_text:
        edges.append({"source": "3", "target": "4"})

    return {"nodes": nodes, "edges": edges}


@router.post(
    "/{chat_id}/share",
    response_model=ShareResponse,
    response_model_by_alias=True,
)
async def create_share(
    chat_id: str,
    body: dict,
    request: Request,
    user_id: str = Depends(get_current_user_id),
):
    _ = (chat_id, user_id)
    forwarded_host = request.headers.get("x-forwarded-host")
    forwarded_proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    base_url = (
        f"{forwarded_proto}://{forwarded_host}"
        if forwarded_host
        else str(request.base_url).rstrip("/")
    )
    share = share_service.create_share(body, base_url)
    return ShareResponse(**share)


@shared_router.get("/{token}", response_model=ChatResponse, response_model_by_alias=True)
async def get_shared_result(token: str):
    payload = share_service.get_share(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return ChatResponse(**payload)
