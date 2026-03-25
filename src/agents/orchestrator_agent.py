"""
OrchestratorAgent coordina SimplifierAgent, ExplainerAgent y CalmEvaluatorAgent
en un patrón de chat grupal usando Microsoft Agent Framework.
"""

from azure.identity.aio import AzureCliCredential
from agent_framework.azure import AzureOpenAIResponsesClient
from agent_framework import Agent
from agent_framework.orchestrations import GroupChatBuilder, GroupChatState
from src.agents.tools.mcp_tool import build_mcp_tool
from src.agents.simplifier_agent import simplifier_agent
from src.agents.explainer_agent import explainer_agent
from src.agents.calm_evaluator_agent import calm_evaluator_agent


async def orchestrator_agent():
    """
    Orchestrador central en el ecosistema DocSimplify.
    Coordina SimplifierAgent, ExplainerAgent y CalmEvaluatorAgent en rondas.
    """
    # Inicializa credenciales y cliente de respuestas de Azure OpenAI
    credential = AzureCliCredential()
    client = AzureOpenAIResponsesClient(credential=credential)

    simplifier = await simplifier_agent()
    explainer = await explainer_agent()
    evaluator = await calm_evaluator_agent()

    orchestrator = (
        GroupChatBuilder()
        .with_participants([simplifier, explainer, evaluator])
        .with_orchestrator_agent(
            name="Orchestrator",
            instructions=(
                "Coordina a los participantes en un ciclo round-robin, "
                "eligiendo al siguiente hablante según la conversación"
            ),
        )
        .with_termination_condition(lambda state: state.turn_count >= 6)
        .build()
    )

    return orchestrator


# Registro de herramientas MCP si aplica
tools = [build_mcp_tool()]
