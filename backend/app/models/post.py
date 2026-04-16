from pydantic import BaseModel, Field
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
    ai_provider_id: Optional[str] = None
    model_name: Optional[str] = None
    auto_publish: bool = False
    thumbnail_source: str = "ai"
    thumbnail_provider_id: Optional[str] = None
    thumbnail_model_name: Optional[str] = None
    target_word_count: Optional[int] = None
    target_section_count: Optional[int] = None
    language: str = Field(default="vietnamese", pattern="^(vietnamese|english)$")


class BulkPostCreate(BaseModel):
    project_id: str
    topics: List[str]
    additional_requests: Optional[str] = ""
    ai_provider_id: Optional[str] = None
    model_name: Optional[str] = None
    auto_publish: bool = False
    thumbnail_source: str = "ai"
    thumbnail_provider_id: Optional[str] = None
    thumbnail_model_name: Optional[str] = None
    target_word_count: Optional[int] = None
    target_section_count: Optional[int] = None
    language: str = Field(default="vietnamese", pattern="^(vietnamese|english)$")


class PostUpdate(BaseModel):
    title: Optional[str] = None
    meta_description: Optional[str] = None
    content: Optional[str] = None
    sections: Optional[List[Section]] = None
    thumbnail_url: Optional[str] = None
    language: Optional[str] = Field(None, pattern="^(vietnamese|english)$")
    research_data: Optional[Dict[str, Any]] = None


class JobInfo(BaseModel):
    job_id: str
    job_type: str  # research, outline, content, thumbnail, publish
    status: str  # pending, running, completed, failed
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TokenUsage(BaseModel):
    research: int = 0
    outline: int = 0
    content: int = 0
    thumbnail: int = 0
    total: int = 0


class PostResponse(BaseModel):
    id: str
    project_id: str
    topic: str
    additional_requests: str
    ai_provider_id: Optional[str] = None
    model_name: Optional[str] = None
    auto_publish: bool = False
    thumbnail_source: str = "ai"
    thumbnail_provider_id: Optional[str] = None
    thumbnail_model_name: Optional[str] = None
    target_word_count: Optional[int] = None
    target_section_count: Optional[int] = None
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
    token_usage: TokenUsage = TokenUsage()
    jobs: List[JobInfo] = []
    created_at: datetime
    wp_post_id: Optional[int] = None
    wp_post_url: Optional[str] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    origin: str = "tool"  # "tool" or "wordpress"
    language: str = "vietnamese"
