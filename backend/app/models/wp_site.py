from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WPSiteCreate(BaseModel):
    name: str
    url: str
    username: str
    api_key: str  # WordPress application password


class WPSiteUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    username: Optional[str] = None
    api_key: Optional[str] = None


class WPSiteResponse(BaseModel):
    id: str
    name: str
    url: str
    username: str
    api_key_preview: str
    created_at: datetime
