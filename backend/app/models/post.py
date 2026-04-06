from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class Section(BaseModel):
    title: str = ""
    content: str = ""
    image_url: Optional[str] = None


class PostCreate(BaseModel):
    project_id: str
    topic: str
    additional_requests: Optional[str] = ""


class BulkPostCreate(BaseModel):
    project_id: str
    topics: List[str]
    additional_requests: Optional[str] = ""


class PostUpdate(BaseModel):
    title: Optional[str] = None
    meta_description: Optional[str] = None
    content: Optional[str] = None
    sections: Optional[List[Section]] = None
    thumbnail_url: Optional[str] = None


class JobInfo(BaseModel):
    job_id: str
    job_type: str  # research, outline, content, thumbnail, section_images, publish
    status: str  # pending, running, completed, failed
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TokenUsage(BaseModel):
    research: int = 0
    outline: int = 0
    content: int = 0
    thumbnail: int = 0
    section_images: int = 0
    total: int = 0


class PostResponse(BaseModel):
    id: str
    project_id: str
    topic: str
    additional_requests: str
    title: Optional[str] = None
    meta_description: Optional[str] = None
    outline: Optional[Dict[str, Any]] = None
    sections: List[Section] = []
    content: Optional[str] = None
    thumbnail_url: Optional[str] = None
    status: str = "draft"  # draft, waiting_approve, published, failed
    research_data: Optional[Dict[str, Any]] = None
    research_done: bool = False
    content_done: bool = False
    thumbnail_done: bool = False
    sections_done: bool = False
    token_usage: TokenUsage = TokenUsage()
    jobs: List[JobInfo] = []
    created_at: datetime
    wp_post_id: Optional[int] = None
