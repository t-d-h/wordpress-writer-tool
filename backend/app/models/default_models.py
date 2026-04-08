from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DefaultModelsCreate(BaseModel):
    writing_provider_id: Optional[str] = None
    writing_model_name: Optional[str] = None
    image_provider_id: Optional[str] = None
    image_model_name: Optional[str] = None
    video_provider_id: Optional[str] = None
    video_model_name: Optional[str] = None


class DefaultModelsUpdate(BaseModel):
    writing_provider_id: Optional[str] = None
    writing_model_name: Optional[str] = None
    image_provider_id: Optional[str] = None
    image_model_name: Optional[str] = None
    video_provider_id: Optional[str] = None
    video_model_name: Optional[str] = None


class DefaultModelsResponse(BaseModel):
    id: str
    writing_provider_id: Optional[str] = None
    writing_model_name: Optional[str] = None
    image_provider_id: Optional[str] = None
    image_model_name: Optional[str] = None
    video_provider_id: Optional[str] = None
    video_model_name: Optional[str] = None
    updated_at: datetime
