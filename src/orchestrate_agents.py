#!/usr/bin/env python3
"""
CLI entrypoint for orchestrating DocSimplify agents.
"""

import asyncio
import argparse

from src.agents.orchestrator_agent import orchestrator_agent


async def main():
    parser = argparse.ArgumentParser(description="DocSimplify orchestrator CLI")
    parser.add_argument(
        "prompt",
        nargs="?",
        default="Simplify this document",
        help="Text or prompt to process",
    )
    args = parser.parse_args()

    orchestrator = await orchestrator_agent()
    # Run the orchestrator and print agent messages
    async for message in orchestrator.run(args.prompt):
        print(message)

    print("Orchestration completed.")


if __name__ == "__main__":
    asyncio.run(main())
