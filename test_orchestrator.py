import asyncio
import os
from agent_framework import AgentSession
from src.config.settings import ClientFactory
from src.agents.common.memory import AccessibilityContextProvider
from src.agents.orchestrator import DocOrchestrator

async def test_implementation():
    """
    Script de prueba para validar la orquestación agéntica y 
    la persistencia del contexto de accesibilidad.
    """
    print("\n" + "="*50)
    print("🚀 INICIANDO PRUEBA DE ORQUESTACIÓN: PROYECTO ELSA")
    print("="*50)

    # 1. Configuración de Infraestructura
    try:
        client = ClientFactory.get_client()
        print("[OK] Cliente de IA inicializado correctamente.")
    except Exception as e:
        print(f"[ERROR] Fallo al inicializar el cliente: {e}")
        return

    # 2. Definición del Perfil de Usuario (Simulación de entrada de base de datos)
    user_profile = {
        "condition": "TDAH", 
        "format": "Puntos clave y analogías"
    }
    
    # 3. Inicialización del Contexto Compartido y Orquestador
    shared_ctx = AccessibilityContextProvider(user_profile)
    orchestrator = DocOrchestrator(client, shared_ctx)
    
    # 4. Creación de la SESIÓN (Donde vive la memoria de corto plazo)
    session = AgentSession()

    # --- FLUJO DE PRUEBA ---

    # ESCENARIO 1: Consulta Inicial (Estado: Normal)
    print("\n--- 📝 ESCENARIO 1: PROCESAMIENTO ESTÁNDAR ---")
    input_1 = "Explícame qué es una cláusula de rescisión en un contrato de alquiler."
    print(f"Usuario: {input_1}")
    
    res1 = await orchestrator.run_pipeline(input_1, session)
    print(f"DocSimplify: {res1}")

    # ESCENARIO 2: Activación de Fatiga Cognitiva
    # El usuario envía una señal que el 'after_run' del ContextProvider debe capturar
    print("\n--- 🥱 ESCENARIO 2: ACTIVACIÓN DE MODO FATIGA ---")
    input_2 = "Uff, esto es demasiado texto para mí ahora mismo, estoy muy cansado 🥱"
    print(f"Usuario: {input_2}")
    
    res2 = await orchestrator.run_pipeline(input_2, session)
    print(f"DocSimplify (Modo Fatiga): {res2}")

    # ESCENARIO 3: Verificación de Persistencia de Contexto
    # Hacemos una nueva pregunta. El sistema debe SEGUIR en modo fatiga automáticamente.
    print("\n--- 🧠 ESCENARIO 3: VALIDACIÓN DE MEMORIA COMPARTIDA ---")
    input_3 = "¿Y cuánto suele costar esa cláusula?"
    print(f"Usuario: {input_3}")
    
    res3 = await orchestrator.run_pipeline(input_3, session)
    print(f"DocSimplify (Persistencia): {res3}")

    # 5. Inspección del Estado de la Sesión
    state = await orchestrator.get_session_state(session)
    print("\n" + "="*50)
    print("📊 RESUMEN DE ESTADO DE SESIÓN")
    print(f"Perfil: {user_profile['condition']}")
    print(f"¿Fatiga detectada?: {state.get('is_fatigued', False)}")
    print("="*50 + "\n")

if __name__ == "__main__":
    # Asegúrate de que las variables de entorno estén cargadas
    if not os.getenv("AZURE_OPENAI_ENDPOINT"):
        print("❌ ERROR: No se detectaron variables de entorno. Revisa tu archivo .env")
    else:
        asyncio.run(test_implementation())