![Brilliant Minds Logo](docs/img/brilliant-minds-logo.png)

# Brilliant Minds

*Learn Your Way. Thrive Your Way*

[![Demo Video](https://img.youtube.com/vi/_-s1Kfu7sLU/0.jpg)](https://www.youtube.com/watch?v=_-s1Kfu7sLU)

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.13-blue)
![Node.js](https://img.shields.io/badge/node.js-18+-green)
![License](https://img.shields.io/badge/license-MIT-green)

**Brilliant Minds** is an AI-powered assistant designed to simplify documents and reduce cognitive load for neurodiverse learners
(ADHD, Autism, Dyslexia). It combines cutting-edge natural language processing with intuitive UI/UX to make content more accessible and easier to understand.

At its core, **Brilliant Minds** integrates intelligent agents such as cognitive profiling, task decomposition, learning support,
and explainability modules to create a responsive and inclusive learning environment. The platform is particularly focused
on supporting neurodiverse learners by optimizing cognitive load, simplifying complex content, and adapting instructional
strategies to individual needs.

By combining advances in artificial intelligence, learning analytics, and pedagogical design,
 Brilliant Minds aims to foster deeper understanding, improve academic performance, and empower both students and educators through transparent, explainable, and human-centered AI systems.

## ✨ Features

- 📄 **Document Simplification** – Converts complex documents into easy-to-understand text
- 🧠 **Cognitive Load Reduction** – Optimized readability for neurodivergent users
- 💬 **Interactive Chat** – Ask questions about simplified content in real-time
- 🎨 **Multiple Themes** – Customizable UI with accessibility-first design
- 🔐 **User Profiles** – Personalized preferences and document history
- 🔍 **RAG-Powered Search** – Grounded retrieval using Azure AI Search
- 📱 **Responsive Design** – Works seamlessly on desktop and mobile
- 🚀 **Demo & Production Modes** – Local testing with mocks or live Azure connections

## 📋 Prerequisites

- **Python** 3.13+
- **Node.js** 18+
- **npm** or **pnpm** (for frontend package management)
- **Azure resources** (for production deployment):
  - Cosmos DB (document storage)
  - Azure Storage Blob (file uploads)
  - Azure AI Search (semantic search)
  - Azure OpenAI (text generation)
  - Document Intelligence (OCR)

## 🚀 Quick Start

### Backend Setup

1. **Install dependencies** in editable mode:

   ```bash
   py -3.13 -m pip install -e .
   ```

2. **Configure environment variables**:

   ```bash
   cp .env.example .env
   ```

   Fill in the required Azure credentials (see [Environment Variables](#-environment-variables) below).

3. **Start the API server** with hot-reload:

   ```bash
   py -3.13 -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
   ```

   - API: <http://localhost:8001>
   - API Documentation (Swagger): <http://localhost:8001/docs>

### Frontend Setup

1. **Navigate to frontend directory**:

   ```bash
   cd frontend
   ```

2. **Install dependencies**:

   ```bash
   npm install
   ```

3. **Start the dev server**:

   ```bash
   npm run dev
   ```

   - Frontend: <http://localhost:3000>
   - By default, it runs in **demo mode** with mock APIs

### Running Both Together

Open two terminals:

**Terminal 1** (Backend):

```bash
py -3.13 -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2** (Frontend):

```bash
cd frontend
npm run dev
```

## 🎛️ Frontend Modes

### Demo Mode (Default)

Perfect for UI/UX prototyping without backend or Azure dependencies:

```bash
cd frontend
npm run dev
```

The frontend uses mock APIs that simulate real backend responses.

### Production Mode (Live API)

To connect to the actual FastAPI backend:

1. **Create `frontend/.env.local`**:

   ```bash
   NEXT_PUBLIC_USE_MOCK_API=false
   NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
   ```

2. **Start both backend and frontend** in separate terminals (see [Quick Start](#-quick-start))

## 🔧 Environment Variables

Copy `.env.example` to `.env` and fill in the following variables:

### Authentication & Security

- `JWT_SECRET_KEY` – Secret key for JWT token signing

### Azure Cosmos DB (User data, documents, chats)

- `COSMOS_ENDPOINT` – Cosmos DB endpoint URL
- `COSMOS_KEY` – Cosmos DB primary key

### Azure Storage (File uploads)

- `AZURE_STORAGE_CONNECTION_STRING` – Connection string for Blob Storage

### Azure AI Search (RAG grounding)

- `AZURE_SEARCH_ENDPOINT` – Search service endpoint
- `AZURE_SEARCH_KEY` – Search service API key

### Azure OpenAI (Text generation & simplification)

- `OPENAI_ENDPOINT` – OpenAI service endpoint
- `OPENAI_API_KEY` – OpenAI API key
- `AI_MODEL_DEPLOYMENT_NAME` – Name of the deployed GPT model

### Azure Document Intelligence (OCR)

- `DOCUMENT_INTELLIGENCE_ENDPOINT` – Document Intelligence endpoint
- `DOCUMENT_INTELLIGENCE_KEY` – Document Intelligence API key

### ⚠️ Important Notes

| Variable | Missing Impact |
|----------|---|
| `COSMOS_*` | User registration, login, profiles, documents, and chats won't work |
| `AZURE_STORAGE_CONNECTION_STRING` | File uploads will fail; no Blob Storage support |
| `AZURE_SEARCH_*` | RAG grounding won't use a live index (fallback to basic search) |
| `DOCUMENT_INTELLIGENCE_*` | OCR falls back to plain text extraction only |

### Requisitos

- Python 3.13
- Node.js 18+

### Backend

```bash
py -3.13 -m pip install -e .
py -3.13 -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

API: `http://localhost:8001`

Swagger: `http://localhost:8001/docs`

### Frontend (`Next.js 16 + React + Tailwind CSS`)

- **App Router** for modern navigation and layouts
- **Server Components** by default with selective `"use client"` boundaries
- **Pages**:
  - Landing page with feature overview
  - Authentication (login/registration)
  - Onboarding flow
  - Dashboard with document management
  - Document viewer & simplification tools
  - Real-time chat interface
- **Responsive design** with Tailwind CSS and accessibility-first approach

### Backend (`FastAPI + Python 3.13`)

- **REST API** endpoints organized by domain:
  - `/api/v1/auth` – Authentication & JWT management
  - `/api/v1/users` – User profiles & preferences
  - `/api/v1/documents` – Document CRUD & metadata
  - `/api/v1/chats` – Chat history & messaging
  - `/api/v1/simplify` – Document simplification pipeline
- **Agent Framework** for AI orchestration
- **Azure Cognitive Services** integration for NLP and document processing
- **Async/await patterns** throughout for scalability

### Infrastructure (Bicep)

- **Azure resources** as code in `/infra/`
- Modular templates for easy deployment and scaling

## 📁 Project Structure

```
brilliant-minds/
├── src/                          # Python backend source
│   ├── agents/                   # AI agent implementations
│   │   ├── orchestrator_agent.py
│   │   ├── simplifier_agent.py
│   │   └── ...
│   ├── api/                      # FastAPI routers & endpoints
│   │   └── v1/
│   ├── config/                   # Configuration management
│   │   └── settings.py
│   ├── core/                     # Core utilities & exceptions
│   │   ├── dependencies.py
│   │   ├── exceptions.py
│   │   └── security.py
│   ├── models/                   # Pydantic schemas & database models
│   │   └── schemas/
│   ├── services/                 # Business logic
│   │   ├── auth_service.py
│   │   ├── search_service.py
│   │   └── ...
│   └── main.py                   # FastAPI app entry point
├── frontend/                     # Next.js application
│   ├── app/                      # App Router pages
│   │   ├── page.tsx              # Landing page
│   │   ├── layout.tsx
│   │   ├── login/
│   │   ├── dashboard/
│   │   ├── documents/
│   │   └── chat/
│   ├── components/               # Reusable React components
│   ├── context/                  # React Context & state management
│   ├── lib/                      # Utilities & helpers
│   │   ├── api.ts
│   │   ├── types.ts
│   │   └── profile.ts
│   └── globals.css               # Global styles
├── infra/                        # Infrastructure as Code (Bicep)
│   ├── main.bicep
│   ├── main.parameters.bicepparam
│   └── modules/
├── tests/                        # Backend tests
│   └── test_auth_service.py
├── pyproject.toml                # Python project metadata
├── .env.example                  # Environment variables template
└── README.md                     # This file
```

### Frontend Linting

Lint TypeScript and React code:

```bash
cd frontend
npm run lint
```

Build for production:

```bash
npm run build
npm run start
```

## 📚 Documentation

- **Backend AGENTS.md** – [AGENTS.md](./AGENTS.md) explains backend conventions, build commands, and code guidelines
- **Frontend AGENTS.md** – [frontend/AGENTS.md](./frontend/AGENTS.md) covers Next.js-specific setup and best practices
- **Docs folder** – [docs/](./docs/) contains architecture deep-dives, design decisions, and agent specifications

## 🤝 Contributing

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feat/my-feature`
3. **Follow code style** guidelines in [AGENTS.md](./AGENTS.md)
4. **Write tests** for new backend features
5. **Run lint & tests** before pushing:

   ```bash
   py -3.13 -m pytest
   cd frontend && npm run lint
   ```

6. **Commit with conventional messages**: `feat: add X`, `fix: resolve Y`
7. **Open a Pull Request** with a clear description

## 📝 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## 👥 Authors & Acknowledgments

**Brilliant Minds** is built with ❤️ by brilliant-minds and the developer community.

- **Design Philosophy**: Accessibility-first, neuro-inclusive UX
- **Tech Stack**: Next.js, FastAPI, Azure Cognitive Services, Bicep
- **Inspiration**: Helping neurodivergent individuals access information with ease

---

## 📞 Support

For questions, issues, or feature requests:

- **Issues**: [GitHub Issues](https://github.com/luiscm17/brilliant-minds/issues)
- **Discussions**: [GitHub Discussions](https://github.com/luiscm17/brilliant-minds/discussions)

---

**Made with accessibility in mind. Brilliant Minds for brilliant people.** 🚀
