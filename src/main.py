# main.py
import asyncio
import os
from azure.identity import DefaultAzureCredential
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework import AgentSession

from src.agents.common.memory import AccessibilityContextProvider
from src.agents.orchestrator import DocOrchestrator

async def run_orchestrator():
    """Lógica principal de ejecución del sistema."""
    
    # 1. Inicializar Cliente (Azure OpenAI como solicitaste)
    client = AzureOpenAIChatClient(
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        credential=DefaultAzureCredential(),
    )

    # 2. Cargar perfil del usuario (Simulado de Cosmos DB)
    user_profile = {"condition": "TDAH", "format": "Visual/Mapas"}
    
    # 3. Inicializar el componente de memoria compartido
    shared_ctx = AccessibilityContextProvider(user_profile)
    
    # 4. Crear el orquestador
    orchestrator = DocOrchestrator(client, shared_ctx)
    
    # 5. Iniciar una sesión persistente
    session = AgentSession()

    # --- SIMULACIÓN DE FLUJO ---
    
    # Primera interacción: Normal
    print("\n--- RONDA 1 ---")
    pregunta = "Explícame qué es una red neuronal"
    respuesta = await orchestrator.run_pipeline(pregunta, session)
    print(f"Resultado 1: {respuesta}")

    # Segunda interacción: El usuario dispara fatiga
    print("\n--- RONDA 2 (Disparo de fatiga) ---")
    pregunta_fatiga = "Uff, es mucho texto, estoy agotado de leer 🥱"
    respuesta_breve = await orchestrator.run_pipeline(pregunta_fatiga, session)
    print(f"Resultado 2 (Modo Fatiga): {respuesta_breve}")

if __name__ == "__main__":
    asyncio.run(run_orchestrator())