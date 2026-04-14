from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    wp_site_id: str


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    wp_site_id: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    title: str
    description: str
    wp_site_id: str
    wp_site_name: Optional[str] = None
    wp_site_url: Optional[str] = None
    created_at: datetime


class TokenUsageResponse(BaseModel):
    research: int = 0
    outline: int = 0
    content: int = 0
    thumbnail: int = 0
    total: int = 0
