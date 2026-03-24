# DocSimplify

Asistente de IA para simplificar documentos y reducir carga cognitiva en personas con dislexia y TDAH.

## Estado actual

- Frontend en `Next.js 16` con App Router
- Backend en `FastAPI`
- El frontend puede funcionar en modo demo con mocks o conectado a la API real

## Levantar el proyecto

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

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:3000`

## Modos del frontend

### Demo local con mocks

Es el modo por defecto. Sirve para revisar el flujo visual completo sin depender del backend ni de Azure.

```bash
cd frontend
npm run dev
```

### Frontend conectado al backend real

Crea `frontend/.env.local` con:

```bash
NEXT_PUBLIC_USE_MOCK_API=false
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
```

Luego levanta backend y frontend en paralelo.

## Variables de entorno del backend

Copia `.env.example` a `.env` y completa al menos:

- `JWT_SECRET_KEY`
- `COSMOS_ENDPOINT`
- `COSMOS_KEY`
- `AZURE_STORAGE_CONNECTION_STRING`
- `AZURE_SEARCH_ENDPOINT`
- `AZURE_SEARCH_KEY`
- `OPENAI_ENDPOINT`
- `OPENAI_API_KEY`
- `AI_MODEL_DEPLOYMENT_NAME`
- `DOCUMENT_INTELLIGENCE_ENDPOINT`
- `DOCUMENT_INTELLIGENCE_KEY`

Notas:

- Sin `COSMOS_*` no funcionarán registro, login, perfil, documentos ni chats reales.
- Sin `AZURE_STORAGE_CONNECTION_STRING` la subida de archivos no podrá usar Blob Storage.
- Sin `AZURE_SEARCH_*` el grounding de RAG no tendrá índice real.
- Sin `DOCUMENT_INTELLIGENCE_*` solo habrá fallback básico para texto plano.

## Arquitectura

### Frontend

- `Next.js + React + Tailwind CSS`
- Landing, login, onboarding, dashboard, documentos y chat

### Backend

- `FastAPI` sobre Python 3.13
- Endpoints en `/api/v1/auth`, `/api/v1/users`, `/api/v1/documents`, `/api/v1/chats`
- Pipeline de simplificación y grounding con servicios Azure

## Estructura

```text
demo-group3/
|-- src/
|   |-- agents/
|   |-- api/
|   |-- config/
|   |-- models/
|   `-- services/
|-- frontend/
`-- infra/
```
