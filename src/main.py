"""FastAPI entrypoint for DocSimplify AI backend.

Registers all routers under /api/v1 and configures CORS and middleware.
"""

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from src.config.settings import CORS_ORIGINS

from src.api.v1.routers import auth, documents, chats

app = FastAPI(
    title="DocSimplify AI",
    description="AI backend to simplify documents for people with dyslexia and ADHD.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

api_router = APIRouter(prefix="/api/v1", tags=["v1"])
for router in (
    auth.router,
    documents.router,
    chats.router,
):
    api_router.include_router(router)
app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "DocSimplify AI"}
