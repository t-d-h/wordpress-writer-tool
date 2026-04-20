from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone


class AIProviderCreate(BaseModel):
    name: str
    provider_type: str = Field(
        ...,
        pattern="^(openai|gemini|anthropic|openai_compatible|openrouter|nvidia_nim)$",
    )
    api_key: str
    api_url: str = ""
    model_name: str = ""


class AIProviderUpdate(BaseModel):
    name: Optional[str] = None
    provider_type: Optional[str] = Field(
        None,
        pattern="^(openai|gemini|anthropic|openai_compatible|openrouter|nvidia_nim)$",
    )
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    model_name: Optional[str] = None


class AIProviderResponse(BaseModel):
    id: str
    name: str
    provider_type: str
    api_key_preview: str  # Only last 4 chars
    api_url: str = ""
    model_name: str = ""
    created_at: datetime
