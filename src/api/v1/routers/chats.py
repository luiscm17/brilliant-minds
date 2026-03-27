from fastapi import APIRouter, Depends, status

from src.core.dependencies import get_current_user_id
from src.models.schemas.chats import ChatMessage, ChatResponse

router = APIRouter(prefix="/chats", tags=["chats"])


@router.post("", response_model=ChatResponse, response_model_by_alias=True)
async def chat_with_agent(
    body: ChatMessage,
    user_id: str = Depends(get_current_user_id),
):
    """
    Punto de conexión con el agente de IA (en desarrollo).
    Este endpoint recibirá los mensajes y delegará la lógica al agente.
    """
    # AQUI SE REALIZARA LA CONEXION CON EL AGENTE
    # Por ahora, se retorna una respuesta vacía o de marcador de posición.
    return ChatResponse(
        simplifiedText="[Agente en desarrollo]",
        explanation="El sistema de agentes está siendo integrado.",
        tone="neutral",
        glossary=[],
    )
