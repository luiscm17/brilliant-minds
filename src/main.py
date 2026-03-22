"""FastAPI entrypoint for DocSimplify AI backend.

Registers all routers under /api/v1 and configures CORS and middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.routers import auth, users, documents, chats, shared

app = FastAPI(
    title="DocSimplify AI",
    description="AI backend to simplify documents for people with dyslexia and ADHD.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(chats.router, prefix="/api/v1")
app.include_router(shared.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "DocSimplify AI"}
