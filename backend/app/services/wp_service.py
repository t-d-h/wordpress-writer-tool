"""
WordPress Service — publish/update posts via the WordPress REST API.
"""

import base64
import httpx
import os
from app.database import wp_sites_col, projects_col
from bson import ObjectId


async def _get_wp_site(project_id: str) -> dict:
    """Get the WordPress site configuration for a project."""
    project = await projects_col.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise Exception(f"Project {project_id} not found")
    wp_site = await wp_sites_col.find_one({"_id": ObjectId(project["wp_site_id"])})
    if not wp_site:
        raise Exception(f"WordPress site not found for project {project_id}")
    return wp_site


def _get_auth_header(username: str, api_key: str) -> dict:
    """Create Basic Auth header for WordPress REST API."""
    credentials = base64.b64encode(f"{username}:{api_key}".encode()).decode()
    return {"Authorization": f"Basic {credentials}"}


async def verify_wp_site(url: str, username: str, api_key: str) -> dict:
    """Verify WordPress site connectivity and credentials.
    Returns {"ok": True} or {"ok": False, "error": "reason"}.
    """
    base_url = url.rstrip("/")

    # Step 1: Check REST API connectivity (no auth needed)
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{base_url}/wp-json/")
    except httpx.ConnectError:
        return {
            "ok": False,
            "error": f"Cannot reach {base_url}. Check the URL is correct and the site is online.",
        }
    except httpx.TimeoutException:
        return {
            "ok": False,
            "error": f"Connection to {base_url} timed out. The site may be slow or unreachable.",
        }
    except httpx.RequestError as e:
        return {"ok": False, "error": f"Failed to connect: {str(e)}"}

    if resp.status_code != 200:
        return {
            "ok": False,
            "error": f"WordPress REST API not available at {base_url}/wp-json/ (HTTP {resp.status_code}). Make sure WordPress REST API is enabled.",
        }

    # Step 2: Verify credentials via authenticated request
    try:
        auth_header = _get_auth_header(username, api_key)
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{base_url}/wp-json/wp/v2/users/me", headers=auth_header
            )
    except httpx.RequestError as e:
        return {"ok": False, "error": f"Failed during credential check: {str(e)}"}

    if resp.status_code == 401 or resp.status_code == 403:
        return {
            "ok": False,
            "error": "Authentication failed. Check your username and application password. Make sure Application Passwords are enabled in your WordPress user profile.",
        }
    if resp.status_code != 200:
        return {
            "ok": False,
            "error": f"Credential verification failed with HTTP {resp.status_code}.",
        }

    return {"ok": True}


async def upload_media(project_id: str, file_path: str, filename: str = None) -> dict:
    """Upload an image to WordPress media library. Returns media object."""
    import logging

    logger = logging.getLogger(__name__)

    logger.info(f"[UPLOAD_MEDIA] Starting upload for project {project_id}")
    logger.info(f"[UPLOAD_MEDIA] File path: {file_path}")

    wp_site = await _get_wp_site(project_id)
    auth_header = _get_auth_header(wp_site["username"], wp_site["api_key"])

    if not filename:
        filename = os.path.basename(file_path)

    logger.info(f"[UPLOAD_MEDIA] Filename: {filename}")

    # Determine content type
    ext = filename.rsplit(".", 1)[-1].lower()
    content_type_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
    }
    content_type = content_type_map.get(ext, "image/png")

    logger.info(f"[UPLOAD_MEDIA] Content type: {content_type}")

    # Check if file exists
    if not os.path.exists(file_path):
        logger.error(f"[UPLOAD_MEDIA] File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")

    # Check file size
    file_size = os.path.getsize(file_path)
    logger.info(f"[UPLOAD_MEDIA] File size: {file_size} bytes")

    # Read file data
    with open(file_path, "rb") as f:
        file_data = f.read()

    logger.info(f"[UPLOAD_MEDIA] Read {len(file_data)} bytes from file")

    url = f"{wp_site['url'].rstrip('/')}/wp-json/wp/v2/media"
    logger.info(f"[UPLOAD_MEDIA] Uploading to: {url}")

    # Use multipart/form-data encoding as required by WordPress REST API
    # Only include Authorization header - let httpx handle Content-Type and Content-Disposition
    files = {"file": (filename, file_data, content_type)}
    headers = {
        "Authorization": auth_header["Authorization"],
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, headers=headers, files=files)
        logger.info(f"[UPLOAD_MEDIA] Response status: {response.status_code}")
        logger.info(f"[UPLOAD_MEDIA] Response body: {response.text[:500]}")
        response.raise_for_status()
        result = response.json()
        logger.info(f"[UPLOAD_MEDIA] Upload successful, media ID: {result.get('id')}")
        return result


async def create_wp_post(
    project_id: str,
    title: str,
    content: str,
    meta_description: str = "",
    thumbnail_media_id: int = None,
    status: str = "draft",
) -> dict:
    """Create a post on WordPress. Returns the WP post object."""
    wp_site = await _get_wp_site(project_id)
    headers = _get_auth_header(wp_site["username"], wp_site["api_key"])
    headers["Content-Type"] = "application/json"

    url = f"{wp_site['url'].rstrip('/')}/wp-json/wp/v2/posts"

    post_data = {
        "title": title,
        "content": content,
        "status": status,
        "excerpt": meta_description,
    }
    if thumbnail_media_id:
        post_data["featured_media"] = thumbnail_media_id

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, headers=headers, json=post_data)
        response.raise_for_status()
        return response.json()


async def update_wp_post(
    project_id: str,
    wp_post_id: int,
    title: str = None,
    content: str = None,
    status: str = None,
    thumbnail_media_id: int = None,
) -> dict:
    """Update an existing WordPress post."""
    wp_site = await _get_wp_site(project_id)
    headers = _get_auth_header(wp_site["username"], wp_site["api_key"])
    headers["Content-Type"] = "application/json"

    url = f"{wp_site['url'].rstrip('/')}/wp-json/wp/v2/posts/{wp_post_id}"

    post_data = {}
    if title:
        post_data["title"] = title
    if content:
        post_data["content"] = content
    if status:
        post_data["status"] = status
    if thumbnail_media_id:
        post_data["featured_media"] = thumbnail_media_id

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, headers=headers, json=post_data)
        response.raise_for_status()
        return response.json()
