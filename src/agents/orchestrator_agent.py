"""Coordinate the TDH-focused orchestration workflow."""

from typing import Optional

from agent_framework import AgentSession
from agent_framework.orchestrations import ConcurrentBuilder

from src.agents.context.history_provider import RedisHistoryProvider
from src.agents.context.custom_context import CustomContextProvider

from src.agents.task_selector_agent import TaskSelectorAgent
from src.agents.simplifier_agent import SimplifierAgent
from src.agents.task_decomposer_agent import TaskDecomposerAgent
from src.agents.learning_support_agent import LearningSupportAgent
from src.agents.focus_assistant_agent import FocusAssistantAgent


class OrchestratorAgent:
    """Runs the ADHD orchestration pipeline from selector to focus assistant."""

    def __init__(self):
        self.history_provider = RedisHistoryProvider()
        self.user_context = CustomContextProvider()

        self.selector = TaskSelectorAgent()
        self.simplifier = SimplifierAgent()
        self.decomposer = TaskDecomposerAgent()
        self.learning_support = LearningSupportAgent()
        self.focus_assistant = FocusAssistantAgent()

    async def run(self, user_query: str, session: AgentSession | None = None):
        """Execute selection, parallel agents, and focus assistant for a query."""
        if session is None:
            session = AgentSession()

        print(
            f"🎼 Initiating the ADHD orchestration workflow... (session: {session.session_id[:8]}...)\n"
        )

        # === STEP 1: Task Selector ===
        print("📋 Running the Task Selector...")
        selector_result = await self.selector.run(user_query, session=session)
        print(f"→ Task Selector: {selector_result}\n")

        # === STEP 2: Fan-out ===
        print("⚙️ Preparing the fan-out...")
        simplifier_agent = await self.simplifier.get_agent()
        decomposer_agent = await self.decomposer.get_agent()
        learning_agent = await self.learning_support.get_agent()

        workflow = ConcurrentBuilder(
            participants=[simplifier_agent, decomposer_agent, learning_agent]
        ).build()

        parallel_context = f"""
        User query:
        {user_query}

        Task Selector decision:
        {selector_result}
        """

        print("🚀 Running the three agents in parallel...\n")
        parallel_results = await workflow.run(
            parallel_context
        )  # No session available here

        # === STEP 3: Focus Assistant (the most important one) ===
        print("🔄 Merging results with the Focus Assistant...")
        final_prompt = f"""
        You are the Focus Assistant. Combine all previous information and generate a final response that is clear, structured, and helpful for an ADHD learner.

        Original user query:
        {user_query}

        Task Selector decision:
        {selector_result}

        Results from the three agents (Simplifier, Task Decomposer, Learning Support):
        {parallel_results}

        Final instructions:
        - Respond warmly and motivationally
        - Use short sentences and bullet points
        - Structure the response with clear numbering
        """

        final_response = await self.focus_assistant.run(final_prompt, session=session)

        print("Orchestration complete.\n")
        return final_response
