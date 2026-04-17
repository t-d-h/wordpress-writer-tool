from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.utils.time_utils import get_now
from pydantic import BaseModel
from app.database import ai_providers_col
from app.models.ai_provider import (
    AIProviderCreate,
    AIProviderUpdate,
    AIProviderResponse,
)

router = APIRouter(prefix="/api/ai-providers", tags=["AI Providers"])


class AIVerifyRequest(BaseModel):
    provider_type: str
    api_key: str
    api_url: str = ""


def format_provider(doc: dict) -> dict:
    return AIProviderResponse(
        id=str(doc["_id"]),
        name=doc["name"],
        provider_type=doc["provider_type"],
        api_key_preview="***" + doc["api_key"][-4:]
        if len(doc["api_key"]) >= 4
        else "***",
        api_url=doc.get("api_url", ""),
        model_name=doc.get("model_name", ""),
        created_at=doc["created_at"],
    ).model_dump()


@router.get("")
async def list_providers():
    providers = []
    async for doc in ai_providers_col.find().sort("created_at", -1):
        providers.append(format_provider(doc))
    return providers


@router.post("/verify")
async def verify_provider(data: AIVerifyRequest):
    """Verify AI provider API key before saving."""
    from app.services.ai_service import verify_api_key

    result = await verify_api_key(data.provider_type, data.api_key, data.api_url)
    if not result["ok"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/{provider_id}")
async def get_provider(provider_id: str):
    doc = await ai_providers_col.find_one({"_id": ObjectId(provider_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Provider not found")
    return format_provider(doc)


@router.post("", status_code=201)
async def create_provider(data: AIProviderCreate):
    from app.services.ai_service import verify_api_key

    result = await verify_api_key(data.provider_type, data.api_key, data.api_url)
    if not result["ok"]:
        raise HTTPException(status_code=400, detail=result["error"])
    doc = {
        **data.model_dump(),
        "created_at": get_now(),
    }
    result = await ai_providers_col.insert_one(doc)
    doc["_id"] = result.inserted_id
    return format_provider(doc)


@router.put("/{provider_id}")
async def update_provider(provider_id: str, data: AIProviderUpdate):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    if any(k in update_data for k in ("api_key", "provider_type")):
        existing = await ai_providers_col.find_one({"_id": ObjectId(provider_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Provider not found")
        from app.services.ai_service import verify_api_key

        verify_provider_type = update_data.get(
            "provider_type", existing["provider_type"]
        )
        verify_api_key_val = update_data.get("api_key", existing["api_key"])
        verify_api_url_val = update_data.get("api_url", existing.get("api_url", ""))
        result = await verify_api_key(
            verify_provider_type, verify_api_key_val, verify_api_url_val
        )
        if not result["ok"]:
            raise HTTPException(status_code=400, detail=result["error"])

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


class FetchModelsRequest(BaseModel):
    api_url: str
    api_key: str


@router.post("/fetch-models")
async def fetch_models(data: FetchModelsRequest):
    """Fetch available models from an OpenAI-compatible provider."""
    from openai import AsyncOpenAI

    base = data.api_url.rstrip("/")
    if not base.endswith("/v1"):
        base = base + "/v1"
    try:
        client = AsyncOpenAI(api_key=data.api_key, base_url=base)
        resp = await client.models.list()
        models = sorted([m.id for m in resp.data])
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch models: {str(e)}")


@router.get("/{provider_id}/models")
async def get_provider_models(provider_id: str):
    """Fetch available models from a stored provider by ID."""
    doc = await ai_providers_col.find_one({"_id": ObjectId(provider_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Provider not found")

    if doc.get("provider_type") != "openai_compatible":
        raise HTTPException(
            status_code=400,
            detail="Only OpenAI-compatible providers support model listing",
        )

    api_url = doc.get("api_url", "")
    api_key = doc.get("api_key", "")

    if not api_url or not api_key:
        raise HTTPException(
            status_code=400, detail="Provider missing API URL or API key"
        )

    from openai import AsyncOpenAI

    base = api_url.rstrip("/")
    if not base.endswith("/v1"):
        base = base + "/v1"
    try:
        client = AsyncOpenAI(api_key=api_key, base_url=base)
        resp = await client.models.list()
        models = sorted([m.id for m in resp.data])
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch models: {str(e)}")
