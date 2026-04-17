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
    writing_input_price_per_m_tokens: float = 0.0
    writing_output_price_per_m_tokens: float = 0.0


class DefaultModelsUpdate(BaseModel):
    writing_provider_id: Optional[str] = None
    writing_model_name: Optional[str] = None
    image_provider_id: Optional[str] = None
    image_model_name: Optional[str] = None
    video_provider_id: Optional[str] = None
    video_model_name: Optional[str] = None
    writing_input_price_per_m_tokens: Optional[float] = None
    writing_output_price_per_m_tokens: Optional[float] = None


class DefaultModelsResponse(BaseModel):
    id: str
    writing_provider_id: Optional[str] = None
    writing_model_name: Optional[str] = None
    image_provider_id: Optional[str] = None
    image_model_name: Optional[str] = None
    video_provider_id: Optional[str] = None
    video_model_name: Optional[str] = None
    writing_input_price_per_m_tokens: float = 0.0
    writing_output_price_per_m_tokens: float = 0.0
    updated_at: datetime
