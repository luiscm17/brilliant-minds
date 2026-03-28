from typing import Dict
from agent_framework import AgentSession

from src.agents.orchestrator_agent import OrchestratorAgent


class OrchestratorService:
    """Expose a FastAPI-friendly wrapper around the OrchestratorAgent."""

    def __init__(self):
        self.orchestrator = OrchestratorAgent()
        self.user_sessions: Dict[str, AgentSession] = {}

    async def get_or_create_session(self, user_id: str) -> AgentSession:
        """Return the existing session for the user or create a new one."""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = AgentSession()
        return self.user_sessions[user_id]

    async def process_message(self, user_id: str, user_message: str) -> str:
        """Run the orchestrator and normalize the final response text."""
        session = await self.get_or_create_session(user_id)

        response = await self.orchestrator.run(user_query=user_message, session=session)

        try:
            if hasattr(response, "text") and response.text:
                return str(response.text).strip()

            if hasattr(response, "messages") and response.messages:
                last_message = response.messages[-1]
                if hasattr(last_message, "text"):
                    return str(last_message.text).strip()
                if hasattr(last_message, "content"):
                    return str(last_message.contents).strip()

            return str(response).strip()

        except Exception as e:
            print(f"[ERROR] Extracting text from AgentResponse: {e}")
            return "Sorry, there was a problem generating the response. Could you try again?"


orchestrator_service = OrchestratorService()
