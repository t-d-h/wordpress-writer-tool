from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from bson import ObjectId
from app.utils.time_utils import get_now
from app.database import wp_sites_col, projects_col
from app.models.wp_site import WPSiteCreate, WPSiteUpdate, WPSiteResponse
from app.dependencies.auth import get_current_user

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
        min_word_count=doc.get("min_word_count", 250),
    ).model_dump()


@router.get("")
async def list_sites(current_user: Annotated[dict, Depends(get_current_user)]):
    sites = []
    async for doc in wp_sites_col.find().sort("created_at", -1):
        sites.append(format_site(doc))
    return sites


@router.post("/verify")
async def verify_site(
    data: WPSiteCreate, current_user: Annotated[dict, Depends(get_current_user)]
):
    """Verify WordPress site connectivity and credentials before saving."""
    from app.services.wp_service import verify_wp_site

    result = await verify_wp_site(data.url, data.username, data.api_key)
    if not result["ok"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/{site_id}")
async def get_site(
    site_id: str, current_user: Annotated[dict, Depends(get_current_user)]
):
    doc = await wp_sites_col.find_one({"_id": ObjectId(site_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Site not found")
    return format_site(doc)


@router.get("/{site_id}/info")
async def get_site_info(
    site_id: str, current_user: Annotated[dict, Depends(get_current_user)]
):
    from app.services.wp_service import get_wp_site_info

    doc = await wp_sites_col.find_one({"_id": ObjectId(site_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Site not found")

    result = await get_wp_site_info(site_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("", status_code=201)
async def create_site(
    data: WPSiteCreate, current_user: Annotated[dict, Depends(get_current_user)]
):
    from app.services.wp_service import verify_wp_site

    result = await verify_wp_site(data.url, data.username, data.api_key)
    if not result["ok"]:
        raise HTTPException(status_code=400, detail=result["error"])
    doc = {
        **data.model_dump(),
        "created_at": get_now(),
    }
    result = await wp_sites_col.insert_one(doc)
    doc["_id"] = result.inserted_id
    return format_site(doc)


@router.put("/{site_id}")
async def update_site(
    site_id: str,
    data: WPSiteUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    existing = await wp_sites_col.find_one({"_id": ObjectId(site_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Site not found")

    if (
        current_user.get("id") != existing.get("created_by")
        and current_user.get("role") != "admin"
    ):
        raise HTTPException(
            status_code=403,
            detail="Only the user who created the site or an admin can update it",
        )

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
async def delete_site(
    site_id: str, current_user: Annotated[dict, Depends(get_current_user)]
):
    existing = await wp_sites_col.find_one({"_id": ObjectId(site_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Site not found")

    if (
        current_user.get("id") != existing.get("created_by")
        and current_user.get("role") != "admin"
    ):
        raise HTTPException(
            status_code=403,
            detail="Only the user who created the site or an admin can delete it",
        )

    result = await wp_sites_col.delete_one({"_id": ObjectId(site_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Site not found")
    return {"message": "Site deleted"}


@router.get("/{site_id}/posts")
async def get_site_posts(
    site_id: str,
    per_page: int = 100,
    page: int = 1,
    status: str = None,
    search: str = None,
    orderby: str = "date",
    order: str = "desc",
    categories: str = None,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Fetch posts from a WordPress site with search, sort, and pagination."""
    from app.services.wp_service import get_wp_posts
    from app.services.wp_cache_service import WPCacheService

    # Parameter validation
    allowed_orderby = ["date", "title", "modified", "relevance"]
    if orderby and orderby not in allowed_orderby:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid orderby parameter. Must be one of: {', '.join(allowed_orderby)}",
        )

    if order and order.lower() not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400, detail="Invalid order parameter. Must be 'asc' or 'desc'"
        )

    if per_page < 1 or per_page > 100:
        raise HTTPException(
            status_code=400, detail="per_page must be between 1 and 100"
        )

    if page < 1:
        raise HTTPException(status_code=400, detail="page must be >= 1")

    doc = await wp_sites_col.find_one({"_id": ObjectId(site_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Site not found")

    project = await projects_col.find_one({"wp_site_id": site_id})
    if not project:
        raise HTTPException(status_code=404, detail="No project found for this site")

    # Per D-09 decision: Search always hits WordPress API (not cached data)
    if search:
        print(f"[CACHE] Search query - bypassing cache, hitting WordPress API")
        result = await get_wp_posts(
            str(project["_id"]),
            per_page,
            page,
            status,
            search,
            orderby,
            order,
            categories,
        )
        return result

    # Hybrid pagination: cache first, WordPress API fallback
    cache_service = WPCacheService()
    cache_key = cache_service.get_cache_key(
        str(project["_id"]), per_page, page, status, orderby, order, categories
    )

    try:
        # Check cache for existing data
        cached = await cache_service.get_cached_posts(cache_key)
        if cached:
            # Check if cache is stale
            is_stale = await cache_service.is_cache_stale(
                cache_key, str(project["_id"])
            )
            if not is_stale:
                print(f"[CACHE] Cache hit for key {cache_key}")
                return cached
            else:
                print(f"[CACHE] Cache stale for key {cache_key}, fetching fresh data")
        else:
            print(f"[CACHE] Cache miss for key {cache_key}")
    except Exception as e:
        print(f"[CACHE_ERROR] Failed to retrieve cache: {str(e)}")
        # Fall back to WordPress API

    # Fetch from WordPress API
    result = await get_wp_posts(
        str(project["_id"]), per_page, page, status, search, orderby, order, categories
    )

    # Update cache
    try:
        await cache_service.cache_posts(cache_key, result["posts"], result["total"])
    except Exception as e:
        print(f"[CACHE_ERROR] Failed to update cache: {str(e)}")
        # Non-critical, continue

    return result

    # Hybrid pagination: cache first, WordPress API fallback
    cache_service = WPCacheService()
    cache_key = cache_service.get_cache_key(
        str(project["_id"]), per_page, page, status, orderby, order, categories
    )

    try:
        # Check cache for existing data
        cached = await cache_service.get_cached_posts(cache_key)
        if cached:
            # Check if cache is stale
            is_stale = await cache_service.is_cache_stale(
                cache_key, str(project["_id"])
            )
            if not is_stale:
                print(f"[CACHE] Cache hit for key {cache_key}")
                return cached
            else:
                print(f"[CACHE] Cache stale for key {cache_key}, fetching fresh data")
        else:
            print(f"[CACHE] Cache miss for key {cache_key}")
    except Exception as e:
        print(f"[CACHE_ERROR] Failed to retrieve cache: {str(e)}")
        # Fall back to WordPress API

    # Fetch from WordPress API
    result = await get_wp_posts(
        str(project["_id"]), per_page, page, status, search, orderby, order, categories
    )

    # Update cache
    try:
        await cache_service.cache_posts(cache_key, result["posts"], result["total"])
    except Exception as e:
        print(f"[CACHE_ERROR] Failed to update cache: {str(e)}")
        # Non-critical, continue

    return result


@router.post("/{site_id}/posts/refresh")
async def refresh_site_posts_cache(
    site_id: str,
    per_page: int = 100,
    page: int = 1,
    status: str = None,
    orderby: str = "date",
    order: str = "desc",
    categories: str = None,
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Manually refresh cached WordPress posts for a site."""
    from app.services.wp_cache_service import WPCacheService

    # Verify site exists
    doc = await wp_sites_col.find_one({"_id": ObjectId(site_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Site not found")

    # Get project
    project = await projects_col.find_one({"wp_site_id": site_id})
    if not project:
        raise HTTPException(status_code=404, detail="No project found for this site")

    # Refresh cache
    cache_service = WPCacheService()
    result = await cache_service.refresh_cache(
        str(project["_id"]),
        per_page,
        page,
        status,
        orderby,
        order,
        search=None,
        categories=categories,
    )

    return result


@router.get("/{site_id}/categories")
async def get_site_categories(
    site_id: str, current_user: Annotated[dict, Depends(get_current_user)]
):
    from app.services.wp_service import get_wp_categories

    doc = await wp_sites_col.find_one({"_id": ObjectId(site_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Site not found")

    result = await get_wp_categories(site_id)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
