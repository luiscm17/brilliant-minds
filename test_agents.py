import asyncio
from agent_framework import Agent, AgentSession
from src.config.settings import ClientFactory
from src.agents.memory.context_provider import AccessibilityContextProvider

async def run_test():
    # 1. Setup inicial
    client = ClientFactory.get_client()
    # Simulamos un usuario con TDAH
    provider = AccessibilityContextProvider(condition="TDAH")
    
    agent = Agent(
        client=client,
        name="DocOrchestrator",
        instructions="Eres un asistente que simplifica documentos complejos.",
        context_providers=[provider]
    )
    
    # Creamos la sesión (aquí vive la memoria del estado)
    session = agent.create_session()

    print("--- 🤖 INICIANDO PRUEBA DE AGENTES ---")

    # TEST 1: Interacción Normal
    print("\n[Usuario]: Hola, simplifica este párrafo: 'La terminología jurídica es intrínsecamente ambigua'.")
    res1 = await agent.run("Simplifica: 'La terminología jurídica es intrínsecamente ambigua'", session=session)
    print(f"[Agente]: {res1}")

    # TEST 2: Disparador de Fatiga
    print("\n[Usuario]: Estoy muy cansado de leer esto, dame algo más fácil 🥱")
    res2 = await agent.run("Estoy muy cansado de leer esto, dame algo más fácil 🥱", session=session)
    print(f"[Agente]: {res2}")

    # TEST 3: Verificación de Persistencia (¿Sigue en modo fatiga?)
    print("\n[Usuario]: ¿Qué es un contrato?")
    res3 = await agent.run("¿Qué es un contrato?", session=session)
    print(f"[Agente]: {res3}")

    # Inspección del estado
    prov_state = session.state.get("doc_accessibility_mem", {})
    print(f"\n[ESTADO FINAL DE SESIÓN]: Fatiga detectada = {prov_state.get('is_fatigued')}")

if __name__ == "__main__":
    asyncio.run(run_test())