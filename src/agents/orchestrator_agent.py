# orchestrations/orchestrator_agent.py
from typing import List

from agent_framework import AgentSession
from agent_framework.orchestrations import ConcurrentBuilder

from src.agents.task_selector_agent import TaskSelectorAgent
from src.agents.simplifier_agent import SimplifierAgent
from src.agents.task_decomposer_agent import TaskDecomposerAgent
from src.agents.learning_support_agent import LearningSupportAgent
from src.agents.focus_assistant_agent import FocusAssistantAgent


class OrchestratorAgent:
    """
    Orquestador para comprensión lectora con TDH.
    Flujo: Task Selector → Fan-out (3 agentes) → Focus Assistant
    """

    def __init__(self):
        self.selector = TaskSelectorAgent()
        self.simplifier = SimplifierAgent()
        self.decomposer = TaskDecomposerAgent()
        self.learning_support = LearningSupportAgent()
        self.focus_assistant = FocusAssistantAgent()

    async def run(self, user_query: str, session: AgentSession | None = None):
        print(f"🎼 Iniciando orquestación para TDH...\nConsulta: {user_query[:120]}...\n")

        # Paso 1: Task Selector
        print("📋 Ejecutando Task Selector...")
        selector_result = await self.selector.run(user_query, session=session)
        print(f"→ Task Selector: {selector_result}\n")

        # Paso 2: Fan-out - Obtener los agentes reales
        print("⚙️ Preparando fan-out...")

        # Obtenemos el agente real de cada wrapper
        simplifier_agent = await self.simplifier.get_agent()
        decomposer_agent = await self.decomposer.get_agent()
        learning_agent = await self.learning_support.get_agent()

        # Creamos el workflow concurrente
        workflow = ConcurrentBuilder(
            participants=[simplifier_agent, decomposer_agent, learning_agent]
        ).build()

        # Contexto para los 3 agentes en paralelo
        parallel_context = f"""
Consulta del usuario:
{user_query}

Decisión del Task Selector:
{selector_result}
"""

        print("🚀 Ejecutando los 3 agentes en paralelo (fan-out)...\n")

        parallel_results = await workflow.run(parallel_context)

        # Paso 3: Fan-in con Focus Assistant
        print("🔄 Combinando resultados con Focus Assistant...")

        final_prompt = f"""
Consulta original del usuario:
{user_query}

Decisión del Task Selector:
{selector_result}

Resultados de los agentes especializados:
{parallel_results}
"""

        final_response = await self.focus_assistant.run(final_prompt, session=session)

        return final_response