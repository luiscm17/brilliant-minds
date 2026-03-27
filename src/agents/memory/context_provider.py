from typing import Any
from agent_framework import BaseContextProvider, SessionContext, AgentSession

class AccessibilityContextProvider(BaseContextProvider):
    """Inyecta el perfil de usuario y detecta fatiga en tiempo real."""
    
    DEFAULT_SOURCE_ID = "doc_accessibility_mem"

    def __init__(self, condition: str = "General"):
        super().__init__(self.DEFAULT_SOURCE_ID)
        self.condition = condition

    async def before_run(self, *, agent: Any, session: AgentSession | None, context: SessionContext, state: dict[str, Any]) -> None:
        """Personaliza las instrucciones antes de la ejecución."""
        is_fatigued = state.get("is_fatigued", False)
        
        # Construcción dinámica de instrucciones sistémicas
        instructions = f"MODO: {'FATIGA (Breve + Emojis)' if is_fatigued else 'ESTÁNDAR'}. "
        instructions += f"PERFIL: {self.condition}. "
        
        context.extend_instructions(self.source_id, instructions)

    async def after_run(self, *, agent: Any, session: AgentSession | None, context: SessionContext, state: dict[str, Any]) -> None:
        """Analiza el input para detectar si el usuario activó el modo fatiga."""
        for msg in context.input_messages:
            text = msg.text.lower() if hasattr(msg, "text") else ""
            if any(trigger in text for trigger in ["cansado", "🥱", "mucho texto", "resumen"]):
                state["is_fatigued"] = True