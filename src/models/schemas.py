"""Pydantic schemas for DocSimplify API request/response models."""

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = Field(min_length=1)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str


# ---------------------------------------------------------------------------
# Users / Profile
# ---------------------------------------------------------------------------

ReadingLevel = Literal["A1", "A2", "B1", "B2", "C1"]
Preset = Literal["Dislexia", "TDAH", "Combinado", "Docente"]
Tone = Literal["calm_supportive", "neutral", "encouraging"]


class UserProfile(BaseModel):
    id: str
    user_id: str
    email: str
    name: str
    reading_level: ReadingLevel = "A2"
    max_sentence_length: int = 12
    tone: Tone = "calm_supportive"
    avoid_words: list[str] = []
    preset: Preset = "TDAH"
    fatigue_history: list[dict] = []
    created_at: Optional[str] = None


class UserProfileUpdate(BaseModel):
    reading_level: Optional[ReadingLevel] = None
    max_sentence_length: Optional[int] = Field(default=None, ge=5, le=30)
    tone: Optional[Tone] = None
    avoid_words: Optional[list[str]] = None
    preset: Optional[Preset] = None


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------

class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    user_id: str
    blob_url: Optional[str] = None
    uploaded_at: str


class DocumentList(BaseModel):
    documents: list[DocumentResponse]
    total: int


# ---------------------------------------------------------------------------
# Chats
# ---------------------------------------------------------------------------

class ChatCreate(BaseModel):
    title: Optional[str] = None


class ChatResponse(BaseModel):
    chat_id: str
    title: Optional[str] = None
    user_id: str
    created_at: str


class WcagReport(BaseModel):
    score: int = Field(ge=0, le=100)
    passed: bool
    issues: list[str] = []


class ChatMessage(BaseModel):
    message: str = Field(min_length=1)
    document_ids: Optional[list[str]] = None


class SimplifiedResponse(BaseModel):
    original_message: str
    simplified_text: str
    explanation: str
    wcag_report: WcagReport
    audio_url: Optional[str] = None
    bee_line_overlay: Optional[str] = None
    preset_used: Optional[str] = None
    reading_level_used: Optional[str] = None
