"""Entry point for DocSimplify CLI.

Demonstrates usage of the TeacherAgent to answer questions
about complex concepts in a simplified way.
"""

import asyncio
from src.agents.teacher_agent import teacher_agent


async def main():
    teacher = await teacher_agent()

    question = "Can you explain what a neural network is?"
    response = await teacher.run(question)

    print("User:", question)
    print("TeacherAgent:", response)


if __name__ == "__main__":
    asyncio.run(main())
