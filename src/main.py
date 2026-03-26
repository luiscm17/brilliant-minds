# main.py
import asyncio
from dotenv import load_dotenv

from src.agents.orchestrator_agent import OrchestratorAgent

load_dotenv()

async def main():
    orchestrator = OrchestratorAgent()

    user_query = """
    Ayúdame a comprender este texto: 
    La fotosíntesis es el proceso por el cual las plantas convierten la energía lumínica 
    en energía química, utilizando dióxido de carbono y agua para producir glucosa y oxígeno.
    """

    result = await orchestrator.run(user_query)

    print("\n" + "="*80)
    print("✅ RESPUESTA FINAL DEL FOCUS ASSISTANT")
    print("="*80)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())