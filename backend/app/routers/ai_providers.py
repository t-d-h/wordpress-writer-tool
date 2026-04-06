from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime, timezone
from app.database import ai_providers_col
from app.models.ai_provider import AIProviderCreate, AIProviderUpdate, AIProviderResponse

router = APIRouter(prefix="/api/ai-providers", tags=["AI Providers"])


def format_provider(doc: dict) -> dict:
    return AIProviderResponse(
        id=str(doc["_id"]),
        name=doc["name"],
        provider_type=doc["provider_type"],
        api_key_preview="***" + doc["api_key"][-4:] if len(doc["api_key"]) >= 4 else "***",
        created_at=doc["created_at"],
    ).model_dump()


@router.get("")
async def list_providers():
    providers = []
    async for doc in ai_providers_col.find().sort("created_at", -1):
        providers.append(format_provider(doc))
    return providers


@router.get("/{provider_id}")
async def get_provider(provider_id: str):
    doc = await ai_providers_col.find_one({"_id": ObjectId(provider_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Provider not found")
    return format_provider(doc)


@router.post("", status_code=201)
async def create_provider(data: AIProviderCreate):
    doc = {
        **data.model_dump(),
        "created_at": datetime.now(timezone.utc),
    }
    result = await ai_providers_col.insert_one(doc)
    doc["_id"] = result.inserted_id
    return format_provider(doc)


@router.put("/{provider_id}")
async def update_provider(provider_id: str, data: AIProviderUpdate):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await ai_providers_col.update_one(
        {"_id": ObjectId(provider_id)}, {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Provider not found")
    doc = await ai_providers_col.find_one({"_id": ObjectId(provider_id)})
    return format_provider(doc)


@router.delete("/{provider_id}")
async def delete_provider(provider_id: str):
    result = await ai_providers_col.delete_one({"_id": ObjectId(provider_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Provider not found")
    return {"message": "Provider deleted"}
