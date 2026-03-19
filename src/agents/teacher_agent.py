from src.agents.base_agent import AzureAIProvider

class TeacherAgent:
    def __init__(self, agent):
        self.agent = agent

    async def run(self, question: str):
        result = await self.agent.run(question)
        return result.text if hasattr(result, "text") else result


async def teacher_agent():
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
