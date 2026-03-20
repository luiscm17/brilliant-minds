"""Teacher agent implementation.

A specialized agent that explains concepts clearly using analogies,
practical examples, and a friendly tone.
"""

from src.agents.base_agent import AzureAIProvider


class TeacherAgent:
    """Wrapper around an agent that provides educational explanations.

    Wraps an underlying agent and provides a simplified interface
    for asking questions and receiving explanations.
    """

    def __init__(self, agent):
        self.agent = agent

    async def run(self, question: str):
        """Ask a question and get an explanation from the agent.

        Args:
            question: The question or concept to be explained.

        Returns:
            Text response with the explanation.
        """
        result = await self.agent.run(question)
        return result.text if hasattr(result, "text") else result


async def teacher_agent():
    """Factory function to create a configured TeacherAgent.

    Returns:
        TeacherAgent instance ready to explain concepts.
    """
    provider = AzureAIProvider()
    agent = await provider.build(
        name="TeacherAgent",
        instructions="""You are a teacher specialized in explaining concepts clearly when students don't understand.

GUIDELINES:
- Use analogies and practical examples
- Structure explanations: concept → example → application
- Break down ideas into smaller parts
- Friendly, patient, encouraging tone
""",
    )
    return TeacherAgent(agent)
