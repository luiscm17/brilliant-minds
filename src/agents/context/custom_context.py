from agent_framework import BaseContextProvider, AgentSession, SessionContext
from typing import Any


class CustomContextProvider(BaseContextProvider):
    """Injects TDH-specific guidance into every agent run."""

    DEFAULT_SOURCE_ID = "user_context"

    def __init__(self):
        super().__init__(self.DEFAULT_SOURCE_ID)

    async def before_run(
        self,
        *,
        agent: Any,
        session: AgentSession | None,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        """Append session-based and TDH-specific instructions before each call."""

        if session and hasattr(session, "state"):
            user_name = session.state.get("user_name")
            if user_name:
                context.extend_instructions(
                    self.source_id,
                    f"The user's name is {user_name}. Be warm, empathetic, and call them by name when it feels natural.",
                )

        context.extend_instructions(
            self.source_id,
            "ADHD user: Use short sentences, bullet points, simple language, a motivating tone, and avoid overwhelming them with information.",
        )

    async def after_run(
        self,
        *,
        agent: Any,
        session: AgentSession | None,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        """Capture user data such as names after each agent invocation."""
        for msg in context.input_messages:
            text = msg.text if hasattr(msg, "text") else ""
            if isinstance(text, str) and "mi nombre es" in text.lower():
                name = (
                    text.lower()
                    .split("mi nombre es")[-1]
                    .strip()
                    .split()[0]
                    .capitalize()
                )
                state["user_name"] = name
