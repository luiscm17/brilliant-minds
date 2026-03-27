# src/agents/common/memory.py
from typing import Any
from agent_framework import BaseContextProvider, SessionContext, AgentSession

class AccessibilityContextProvider(BaseContextProvider):
    """Componente reutilizable de Memoria Cognitiva para todos los agentes."""
    DEFAULT_SOURCE_ID = "shared_accessibility_ctx"

    def __init__(self, user_profile: dict):
        super().__init__(self.DEFAULT_SOURCE_ID)
        self.profile = user_profile

    async def before_run(
        self,
        *,
        agent: Any,
        session: AgentSession | None,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        """Inyecta perfil y estado de fatiga antes de cada ejecución."""
        is_fatigued = state.get("is_fatigued", False)
        
        # Instrucciones base de accesibilidad
        instructions = (
            f"DATOS DE USUARIO: Condición: {self.profile.get('condition', 'General')}. "
            f"Preferencia: {self.profile.get('format', 'Texto claro')}. "
        )
        
        # Cambio dinámico por fatiga
        if is_fatigued:
            instructions += "ESTADO: FATIGA DETECTADA. Prioriza brevedad extrema, puntos clave y emojis."
        else:
            instructions += "ESTADO: ESTÁNDAR. Proporciona explicaciones estructuradas."

        context.extend_instructions(self.source_id, instructions)

    async def after_run(
        self,
        *,
        agent: Any,
        session: AgentSession | None,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        """Detecta si el usuario activó señales de fatiga en su mensaje."""
        for msg in context.input_messages:
            text = msg.text.lower() if hasattr(msg, "text") else ""
            if any(trigger in text for trigger in ["cansado", "mucho texto", "🥱", "resumen corto"]):
                state["is_fatigued"] = True