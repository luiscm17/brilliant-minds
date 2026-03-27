import os
import asyncio
from typing import Optional
from agent_framework import Agent, AgentSession

class DocOrchestrator:
    """
    Orquestador central del ecosistema DocSimplify.
    Coordina agentes especialistas compartiendo un contexto cognitivo común.
    """

    def __init__(self, client, shared_context):
        """
        Inicia el orquestador.
        :param client: Instancia de AzureOpenAIChatClient o OpenAIChatClient.
        :param shared_context: Instancia de AccessibilityContextProvider.
        """
        self.client = client
        self.shared_context = shared_context
        
        # IDs de agentes desde variables de entorno (Azure AI Foundry)
        self.brain_id = os.getenv("BRAIN_ID")
        self.teacher_id = os.getenv("TEACHER_ID")

    async def run_pipeline(self, user_input: str, session: AgentSession) -> str:
        """
        Ejecuta el flujo de trabajo: Brain (Análisis) -> Teacher (Simplificación).
        
        Ambos agentes usan el mismo shared_context, por lo que si uno detecta 
        fatiga, el siguiente ajustará su respuesta automáticamente.
        """
        
        # 1. Instanciar Agente de Análisis (The Brain)
        # Nota: En RC5 se usa 'client' para pasar el objeto de conexión
        brain_agent = Agent(
            client=self.client, 
            name="TheBrain",
            instructions="Analiza el documento...",
            context_providers=[self.shared_context]
        )

        # 2. Instanciar Agente Pedagógico (Teacher Agent)
        teacher_agent = Agent(
            client=self.client,
            name="TeacherAgent",
            instructions=(
                "Eres un experto en simplificación cognitiva. Tu tarea es explicar "
                "conceptos técnicos de forma clara, usando analogías y lenguaje sencillo."
            ),
            context_providers=[self.shared_context]
        )

        try:
            # FASE 1: El Cerebro procesa la información técnica
            print(f"[*] Ejecutando análisis con The Brain...")
            analysis_output = await brain_agent.run(user_input, session=session)
            
            # FASE 2: El Profesor simplifica basándose en el análisis previo
            # Se le pasa el output del Brain para que lo transforme
            print(f"[*] Ejecutando simplificación con Teacher Agent...")
            prompt_pedagogico = (
                f"Basándote en este análisis técnico: '{analysis_output}', "
                f"explícale al usuario los puntos más importantes de forma sencilla."
            )
            
            final_response = await teacher_agent.run(prompt_pedagogico, session=session)
            
            return final_response

        except Exception as e:
            return f"Error en la orquestación del pipeline: {str(e)}"

    async def get_session_state(self, session: AgentSession):
        """Devuelve el estado actual de la memoria almacenado en la sesión."""
        return session.state.get(self.shared_context.source_id, {})