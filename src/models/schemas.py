"""Pydantic schemas for the API contract consumed by the frontend."""

from typing import Literal, Optional

from pydantic import BaseModel, Field, ConfigDict


class ApiModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class UserCreate(ApiModel):
    email: str
    password: str = Field(min_length=6)
    name: str = Field(min_length=1)


class UserLogin(ApiModel):
    email: str
    password: str


class AuthUser(ApiModel):
    user_id: str = Field(alias="userId")
    email: str
    name: str


class AuthResponse(ApiModel):
    token: str
    user_id: str = Field(alias="userId")
    user: AuthUser


# ---------------------------------------------------------------------------
# Users / Profile
# ---------------------------------------------------------------------------


ReadingLevel = Literal["A1", "A2", "B1", "C1"]
AccessibilityPreset = Literal["dyslexia", "adhd", "combined", "custom"]
Tone = Literal["calm_supportive", "neutral_clear"]
CognitivePriority = Literal[
    "focus",
    "calm",
    "contrast",
    "short_sentences",
    "step_by_step",
]


class UserProfile(ApiModel):
    has_adhd: bool = Field(alias="hasAdhd")
    has_dyslexia: bool = Field(alias="hasDyslexia")
    reading_level: ReadingLevel = Field(alias="readingLevel")
    preset: AccessibilityPreset
    max_sentence_length: int = Field(alias="maxSentenceLength", ge=5, le=30)
    tone: Tone
    priorities: list[CognitivePriority] = Field(default_factory=list)


class UserProfileUpdate(ApiModel):
    has_adhd: Optional[bool] = Field(default=None, alias="hasAdhd")
    has_dyslexia: Optional[bool] = Field(default=None, alias="hasDyslexia")
    reading_level: Optional[ReadingLevel] = Field(default=None, alias="readingLevel")
    preset: Optional[AccessibilityPreset] = None
    max_sentence_length: Optional[int] = Field(
        default=None, alias="maxSentenceLength", ge=5, le=30
    )
    tone: Optional[Tone] = None
    priorities: Optional[list[CognitivePriority]] = None


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------


DocumentStatus = Literal["uploaded", "processing", "completed", "error"]


class DocumentItem(ApiModel):
    document_id: str = Field(alias="documentId")
    filename: str
    status: DocumentStatus


class DocumentUploadResult(DocumentItem):
    success: bool = True


# ---------------------------------------------------------------------------
# Chats
# ---------------------------------------------------------------------------


class ChatCreate(ApiModel):
    title: Optional[str] = None


class CreateChatResponse(ApiModel):
    chat_id: str = Field(alias="chatId")


class ChatMessage(ApiModel):
    message: str = Field(min_length=1)
    document_ids: Optional[list[str]] = Field(default=None, alias="documentIds")
    fatigue_level: int = Field(default=0, ge=0, le=2, alias="fatigueLevel")
    target_language: Optional[str] = Field(default=None, alias="targetLanguage")


class ChatResponse(ApiModel):
    original_message: Optional[str] = Field(default=None, alias="originalMessage")
    simplified_text: str = Field(alias="simplifiedText")
    explanation: str
    tone: str
    audio_url: Optional[str] = Field(default=None, alias="audioUrl")
    bee_line_overlay: Optional[bool] = Field(default=None, alias="beeLineOverlay")
    wcag_report: Optional[str] = Field(default=None, alias="wcagReport")
    preset_used: Optional[str] = Field(default=None, alias="presetUsed")
    reading_level_used: Optional[str] = Field(default=None, alias="readingLevelUsed")
    emoji_summary: Optional[str] = Field(default=None, alias="emojiSummary")
    glossary: list[dict] = Field(default_factory=list)
    searches_performed: list[str] = Field(default_factory=list, alias="searchesPerformed")


class ShareResponse(ApiModel):
    share_token: str = Field(alias="shareToken")
    share_url: str = Field(alias="shareUrl")


class WcagReport(ApiModel):
    score: int = Field(ge=0, le=100)
    passed: bool
    issues: list[str] = Field(default_factory=list)
