from agent_framework import (
    Agent,
    AgentExecutorResponse,
    AgentResponseUpdate,
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)

from src.agents.triage_agent import triage_agent
from src.agents.focus_assistant_agent import focus_assistant_agent
from src.agents.learning_support_agent import learning_support_agent
from src.agents.task_descomposer_agent import task_descomposer_agent
from src.agents.explainability_agent import explainability_agent
from src.agents.simplifier_agent import simplifier_agent
from src.agents.providers.azure_ai_project import AIProjectProvider


class AgentOrchestrator:
    """Orquestador con estado persistente en Redis."""

    def __init__(self, redis_url="redis://localhost:6379"):
        self.workflow = None
        self.redis_url = redis_url
        self.provider = AIProjectProvider()

    async def setup(self):
        triage = await triage_agent(self.provider)
        focus_assistant = await focus_assistant_agent(self.provider)
        learning_support = await learning_support_agent(self.provider)
        task_descomposer = await task_descomposer_agent(self.provider)
        explainability = await explainability_agent(self.provider)
        simplifier = await simplifier_agent(self.provider)

        workflow_builder = (
            WorkflowBuilder(
                name="docsimplify_workflow",
                description="Workflow for Docsimplify AI Assistant",
                start_executor=task_descomposer,
                output_executors=[focus_assistant],
            )
            .add_fan_out_edges(
                task_descomposer, [learning_support, explainability, simplifier]
            )
            .add_fan_in_edges(
                [learning_support, explainability, simplifier], focus_assistant
            )
            .build()
        )
        self.workflow = workflow_builder.as_agent(
            name="docsimplify_orchestrator",
            description="Orchestrator for Docsimplify AI Assistant",
        )

    async def run(self, prompt: str, session_id: str | None = None):
        """Execute the orchestrator workflow with the provided prompt."""

        if not self.workflow:
            raise RuntimeError("Agent workflow is not initialized. Call setup() first.")

        context = {"session_id": session_id} if session_id else None
        result = await self.workflow.run(prompt, context=context)
        return getattr(result, "text", result)
