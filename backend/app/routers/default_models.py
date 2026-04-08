from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime, timezone
from pydantic import BaseModel
from app.database import default_models_col, ai_providers_col
from app.models.default_models import (
    DefaultModelsCreate,
    DefaultModelsUpdate,
    DefaultModelsResponse,
)

router = APIRouter(prefix="/api/default-models", tags=["Default Models"])


def format_default_models(doc: dict) -> dict:
    return DefaultModelsResponse(
        id=str(doc["_id"]),
        writing_provider_id=doc.get("writing_provider_id"),
        writing_model_name=doc.get("writing_model_name"),
        image_provider_id=doc.get("image_provider_id"),
        image_model_name=doc.get("image_model_name"),
        video_provider_id=doc.get("video_provider_id"),
        video_model_name=doc.get("video_model_name"),
        updated_at=doc.get("updated_at", datetime.now(timezone.utc)),
    ).model_dump()


@router.get("")
async def get_default_models():
    """Get current default models settings (singleton)."""
    doc = await default_models_col.find_one()
    if not doc:
        return {
            "id": "",
            "writing_provider_id": None,
            "writing_model_name": None,
            "image_provider_id": None,
            "image_model_name": None,
            "video_provider_id": None,
            "video_model_name": None,
            "updated_at": None,
        }
    return format_default_models(doc)


@router.put("")
async def update_default_models(data: DefaultModelsUpdate):
    """Update default models settings (create if doesn't exist)."""
    update_data = {
        k: v for k, v in data.model_dump().items() if v is not None and v != ""
    }

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Validate provider_ids exist
    provider_fields = ["writing_provider_id", "image_provider_id", "video_provider_id"]
    for field in provider_fields:
        if field in update_data and update_data[field]:
            provider = await ai_providers_col.find_one(
                {"_id": ObjectId(update_data[field])}
            )
            if not provider:
                raise HTTPException(
                    status_code=400, detail=f"Provider not found: {update_data[field]}"
                )

    update_data["updated_at"] = datetime.now(timezone.utc)

    existing = await default_models_col.find_one()
    if existing:
        result = await default_models_col.update_one(
            {"_id": existing["_id"]}, {"$set": update_data}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Default models not found")
        doc = await default_models_col.find_one({"_id": existing["_id"]})
    else:
        result = await default_models_col.insert_one(update_data)
        doc = await default_models_col.find_one({"_id": result.inserted_id})

    return format_default_models(doc)
