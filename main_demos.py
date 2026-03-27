#!/usr/bin/env python3
"""
Demo entrypoint for orchestrator_agent via CLI.

Run with: python main_demos.py "Your prompt here" [session_id]
"""

import asyncio
import sys

from src.agents.orchestrator_agent import AgentOrchestrator


async def main():
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
    else:
        prompt = input("Enter prompt: ").strip()
    if len(sys.argv) > 2:
        session_id = sys.argv[2]
    else:
        session_id = input("Session ID (optional): ").strip() or None

    orchestrator = AgentOrchestrator()
    await orchestrator.setup()
    result = await orchestrator.run(prompt, session_id)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
