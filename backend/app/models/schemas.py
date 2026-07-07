from typing import Literal

from pydantic import BaseModel, Field


ContentType = Literal["text", "link", "image"]


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class MessageIn(BaseModel):
    user_id: str = Field(..., min_length=1)
    content_type: ContentType = "text"
    content: str = Field(..., min_length=1)
    source_url: str | None = None
    user_note: str | None = None


class KnowledgeAnalysis(BaseModel):
    title: str
    source: str = "user_input"
    original_url: str | None = None
    summary: str
    category: str
    tags: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    user_note: str | None = None
    model: str | None = None
    token_usage: TokenUsage | None = None


class KnowledgeCreate(BaseModel):
    user_id: str
    raw_content: str
    analysis: KnowledgeAnalysis


class KnowledgeSaveResult(BaseModel):
    saved: bool
    knowledge_id: str | None = None
    storage: Literal["feishu", "dry_run"] = "dry_run"
    message: str


class MessageProcessResult(BaseModel):
    saved: bool
    knowledge_id: str | None = None
    storage: str
    analysis: KnowledgeAnalysis


class SearchResultItem(BaseModel):
    id: str
    title: str
    summary: str
    category: str
    tags: list[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    items: list[SearchResultItem]
    message: str
