from typing import Optional
from pydantic import Field
from src.models.schemas.base import ApiModel


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
