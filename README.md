# DocSimplify

AI assistant to simplify documents designed for people with dyslexia and ADHD.

## 🎯 Purpose

Transform dense documents (PDF, Word, texts) into clear and accessible versions with:

- Adjustable reading levels (A1-C1)
- Bullet point summaries
- Accessible audio
- Calm explanations of each change

## 🏗️ Architecture

### Frontend

- **React + Tailwind** on Azure App Service
- OpenDyslexic fonts and BeeLine Reader
- Immersive Reader SDK integration
- WCAG 2.2 compliant

### Backend (Multi-Agent System)

- **Microsoft Foundry Agent Service** as orchestrator
  - **Parser Agent** - Processes documents with Azure Document Intelligence
  - **Simplifier Agent** - Simplifies text with GPT-4o
  - **Explainer Agent** - Generates calm explanations
  - **Accessibility Agent** - Applies accessible formats
  - **Validator Agent** - Validates WCAG and security

### Azure Services Used

1. App Service (frontend)
2. Foundry Agent Service (orchestration)
3. Azure Functions (backend)
4. Azure OpenAI
5. Azure Document Intelligence
6. Cosmos DB + Blob Storage
7. Azure AI Search
8. Content Safety Studio
9. Responsible AI Toolbox
10. Azure Key Vault
11. Azure Monitor

## 👥 Users

- **Students/Employees** with dyslexia or ADHD
- **Teachers/Managers** to create inclusive materials
- **Administrators** to configure accessibility profiles

## 🛠️ Project Structure

```text
DocSimplify/
├── frontend/          # React + Tailwind
├── agents/            # Microsoft Agent Framework
├── functions/         # Azure Functions (backend)
├── infrastructure/    # Bicep/Terraform
├── shared/           # Shared code
└── docs/             # Documentation
```

## 🚀 Deployment

```bash
azd up  # Deploy entire solution
```

## 📋 Requirements

- Node.js 18+
- Azure CLI
- Azure Developer CLI (azd)
- Azure Subscription

## Test agent memory
pip install azure-ai-projects azure-identity python-dotenv agent-framework
python -c "from agent_framework.azure import AzureOpenAIChatClient; import inspect; print(inspect.signature(AzureOpenAIChatClient.__init__))"
python test_orchestrator.py

