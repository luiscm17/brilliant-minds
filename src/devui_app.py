# devui_app.py
import os
import asyncio
# from src.config.settings import AgentSettings
from dotenv import load_dotenv

# Cargar variables de entorno primero
load_dotenv()

if not os.getenv("AZURE_AI_PROJECT_ENDPOINT") or not os.getenv("AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME"):
    print("❌ Error: Faltan AZURE_AI_PROJECT_ENDPOINT o AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME en tu archivo .env")
    exit(1)

print("✅ Variables de entorno cargadas correctamente.\n")

from agent_framework.devui import serve
from agent_framework.orchestrations import ConcurrentBuilder

# Importar tus clases
from src.agents.task_selector_agent import TaskSelectorAgent
from src.agents.simplifier_agent import SimplifierAgent
from src.agents.task_decomposer_agent import TaskDecomposerAgent
from src.agents.learning_support_agent import LearningSupportAgent
from src.agents.focus_assistant_agent import FocusAssistantAgent

from src.agents.orchestrator_agent import OrchestratorAgent


async def build_fanout_workflow():
    """Crea el workflow de fan-out para que DevUI lo muestre como grafo."""
    print("🔨 Creando workflow FanOut_TDH_Comprension_Lectora...")

    s = SimplifierAgent()
    d = TaskDecomposerAgent()
    l = LearningSupportAgent()

    real_agents = await asyncio.gather(
        s.get_agent(),
        d.get_agent(),
        l.get_agent()
    )

    workflow = ConcurrentBuilder(
        participants=real_agents,
    ).build()

    return workflow


def main():
    """Función síncrona que prepara todo y lanza serve()"""
    # Crear agentes individuales
    selector = TaskSelectorAgent()
    simplifier = SimplifierAgent()
    decomposer = TaskDecomposerAgent()
    learning_support = LearningSupportAgent()
    focus_assistant = FocusAssistantAgent()

    # Crear el workflow fan-out
    fanout_workflow = asyncio.run(build_fanout_workflow())

    # Tu orquestador completo
    orchestrator = OrchestratorAgent()

    entities = [
        selector,
        simplifier,
        decomposer,
        learning_support,
        focus_assistant,
        fanout_workflow,           # ← Esto te permite ver el fan-out visualmente
        orchestrator,
    ]

    print("🌐 Iniciando DevUI...")
    print("   → Abre tu navegador en: http://127.0.0.1:8080")
    print("   Prueba especialmente el workflow 'FanOut_TDH_Comprension_Lectora'\n")

    # Lanzamos serve de forma síncrona (fuera del event loop principal)
    serve(
        entities=entities,
        auto_open=True,
        port=8080,
        # tracing_enabled=True,     # descomenta si quieres trazas detalladas
    )


if __name__ == "__main__":
    main()