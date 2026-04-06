from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone


class AIProviderCreate(BaseModel):
    name: str
    provider_type: str = Field(..., pattern="^(openai|gemini|anthropic)$")
    api_key: str


class AIProviderUpdate(BaseModel):
    name: Optional[str] = None
    provider_type: Optional[str] = Field(None, pattern="^(openai|gemini|anthropic)$")
    api_key: Optional[str] = None


class AIProviderResponse(BaseModel):
    id: str
    name: str
    provider_type: str
    api_key_preview: str  # Only last 4 chars
    created_at: datetime
