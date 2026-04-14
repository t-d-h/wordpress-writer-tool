from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime, timezone
from app.database import wp_sites_col, projects_col
from app.models.wp_site import WPSiteCreate, WPSiteUpdate, WPSiteResponse

router = APIRouter(prefix="/api/wp-sites", tags=["WordPress Sites"])


def format_site(doc: dict) -> dict:
    return WPSiteResponse(
        id=str(doc["_id"]),
        name=doc["name"],
        url=doc["url"],
        username=doc["username"],
        api_key_preview="***" + doc["api_key"][-4:]
        if len(doc["api_key"]) >= 4
        else "***",
        created_at=doc["created_at"],
    ).model_dump()


@router.get("")
async def list_sites():
    sites = []
    async for doc in wp_sites_col.find().sort("created_at", -1):
        sites.append(format_site(doc))
    return sites


@router.post("/verify")
async def verify_site(data: WPSiteCreate):
    """Verify WordPress site connectivity and credentials before saving."""
    from app.services.wp_service import verify_wp_site

    result = await verify_wp_site(data.url, data.username, data.api_key)
    if not result["ok"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/{site_id}")
async def get_site(site_id: str):
    doc = await wp_sites_col.find_one({"_id": ObjectId(site_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Site not found")
    return format_site(doc)


@router.post("", status_code=201)
async def create_site(data: WPSiteCreate):
    from app.services.wp_service import verify_wp_site

    result = await verify_wp_site(data.url, data.username, data.api_key)
    if not result["ok"]:
        raise HTTPException(status_code=400, detail=result["error"])
    doc = {
        **data.model_dump(),
        "created_at": datetime.now(timezone.utc),
    }
    result = await wp_sites_col.insert_one(doc)
    doc["_id"] = result.inserted_id
    return format_site(doc)


@router.put("/{site_id}")
async def update_site(site_id: str, data: WPSiteUpdate):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    if any(k in update_data for k in ("url", "username", "api_key")):
        existing = await wp_sites_col.find_one({"_id": ObjectId(site_id)})
        if not existing:
            raise HTTPException(status_code=404, detail="Site not found")
        from app.services.wp_service import verify_wp_site

        verify_url = update_data.get("url", existing["url"])
        verify_username = update_data.get("username", existing["username"])
        verify_api_key = update_data.get("api_key", existing["api_key"])
        result = await verify_wp_site(verify_url, verify_username, verify_api_key)
        if not result["ok"]:
            raise HTTPException(status_code=400, detail=result["error"])

    result = await wp_sites_col.update_one(
        {"_id": ObjectId(site_id)}, {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Site not found")
    doc = await wp_sites_col.find_one({"_id": ObjectId(site_id)})
    return format_site(doc)


@router.delete("/{site_id}")
async def delete_site(site_id: str):
    result = await wp_sites_col.delete_one({"_id": ObjectId(site_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Site not found")
    return {"message": "Site deleted"}


@router.get("/{site_id}/posts")
async def get_site_posts(
    site_id: str, per_page: int = 100, page: int = 1, status: str = None
):
    """Fetch posts from a WordPress site."""
    from app.services.wp_service import get_wp_posts

    doc = await wp_sites_col.find_one({"_id": ObjectId(site_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Site not found")

    project = await projects_col.find_one({"wp_site_id": site_id})
    if not project:
        raise HTTPException(status_code=404, detail="No project found for this site")

    result = await get_wp_posts(str(project["_id"]), per_page, page, status)

    return result
