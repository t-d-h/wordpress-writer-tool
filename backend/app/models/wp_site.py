from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class WPSiteCreate(BaseModel):
    name: str
    url: str
    username: str
    api_key: str  # WordPress application password
    min_word_count: int = Field(250, gt=0)


class WPSiteUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    username: Optional[str] = None
    api_key: Optional[str] = None
    min_word_count: Optional[int] = Field(None, gt=0)


class WPSiteResponse(BaseModel):
    id: str
    name: str
    url: str
    username: str
    api_key_preview: str
    created_at: datetime
    min_word_count: int


class WPPostResponse(BaseModel):
    id: int
    title: str
    link: str
    date: str
    modified: str
    status: str
    categories: List[dict] = []
    tags: List[dict] = []
    excerpt: str = ""
    author: int = 0
