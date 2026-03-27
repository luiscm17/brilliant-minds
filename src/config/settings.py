# src/config/settings.py
import os
from dotenv import load_dotenv
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework.openai import OpenAIChatClient

load_dotenv()

class ClientFactory:
    """Fábrica de clientes usando API Key para evitar problemas de DefaultAzureCredential."""
    
    @staticmethod
    def get_client():
        use_azure = os.getenv("USE_AZURE", "true").lower() == "true"
        
        if use_azure:
            # Usamos api_key directamente para saltar la validación de DefaultAzureCredential
            return AzureOpenAIChatClient(
                endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                api_key=os.getenv("AZURE_OPENAI_KEY") # Asegúrate de tener esta variable en tu .env
            )
        else:
            return OpenAIChatClient(
                api_key=os.getenv("OPENAI_API_KEY"),
                model=os.getenv("OPENAI_MODEL", "gpt-4o")
            )