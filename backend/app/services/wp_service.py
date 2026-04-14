"""
WordPress Service — publish/update posts via the WordPress REST API.
"""

import asyncio
import base64
import httpx
import os
from datetime import datetime
from app.database import wp_sites_col, projects_col
from bson import ObjectId


def _format_date(date_string: str) -> str:
    """Format WordPress date string to DD MMMM YYYY format.

    Args:
        date_string: ISO 8601 date string from WordPress API

    Returns:
        Formatted date string (e.g., "14 April 2026") or empty string on error
    """
    if not date_string:
        return ""
    try:
        dt = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        return dt.strftime("%d %B %Y")
    except Exception as e:
        print(f"[FORMAT_DATE_ERROR] Failed to format date '{date_string}': {str(e)}")
        return ""


def _extract_categories(embedded: dict) -> list:
    """Extract category names from WordPress _embedded data.

    Args:
        embedded: _embedded dict from WordPress API response

    Returns:
        List of category names or empty list if not found
    """
    if not embedded:
        return []
    try:
        wp_terms = embedded.get("wp:term", [])
        if len(wp_terms) < 1 or not wp_terms[0]:
            return []
        return [term.get("name", "") for term in wp_terms[0] if term.get("name")]
    except Exception as e:
        print(f"[EXTRACT_CATEGORIES_ERROR] Failed to extract categories: {str(e)}")
        return []


def _extract_tags(embedded: dict) -> list:
    """Extract tag names from WordPress _embedded data.

    Args:
        embedded: _embedded dict from WordPress API response

    Returns:
        List of tag names or empty list if not found
    """
    if not embedded:
        return []
    try:
        wp_terms = embedded.get("wp:term", [])
        if len(wp_terms) < 2 or not wp_terms[1]:
            return []
        return [term.get("name", "") for term in wp_terms[1] if term.get("name")]
    except Exception as e:
        print(f"[EXTRACT_TAGS_ERROR] Failed to extract tags: {str(e)}")
        return []


def _generate_edit_url(site_url: str, post_id: int) -> str:
    """Generate WordPress admin edit URL for a post.

    Args:
        site_url: WordPress site URL
        post_id: Post ID

    Returns:
        Full edit URL string or empty string on error
    """
    if not site_url or not post_id:
        return ""
    try:
        base_url = site_url.rstrip("/")
        return f"{base_url}/wp-admin/post.php?post={post_id}&action=edit"
    except Exception as e:
        print(f"[GENERATE_EDIT_URL_ERROR] Failed to generate edit URL: {str(e)}")
        return ""


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


async def fetch_with_retry(
    url: str, headers: dict, params: dict, max_retries: int = 3
) -> dict:
    """Fetch with exponential backoff on rate limit errors.

    Args:
        url: WordPress REST API endpoint URL
        headers: Request headers (including auth)
        params: Query parameters
        max_retries: Maximum number of retry attempts

    Returns:
        dict with 'posts' list and 'total' count

    Raises:
        httpx.HTTPStatusError: If request fails after max retries
    """
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.get(url, headers=headers, params=params)

                if response.status_code == 429:
                    # Rate limit exceeded, wait with exponential backoff
                    wait_time = 2**attempt  # 1, 2, 4 seconds
                    print(
                        f"[RATE_LIMIT] Too many requests, waiting {wait_time}s before retry {attempt + 1}/{max_retries}"
                    )
                    await asyncio.sleep(wait_time)
                    continue

                response.raise_for_status()
                posts = response.json()
                total = int(response.headers.get("X-WP-Total", len(posts)))
                return {"posts": posts, "total": total}

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 and attempt < max_retries - 1:
                continue
            raise
        except httpx.RequestError as e:
            print(f"[REQUEST_ERROR] Failed to fetch posts: {str(e)}")
            raise

    raise Exception(
        f"Failed to fetch posts after {max_retries} retries due to rate limiting"
    )


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


async def get_wp_posts(
    project_id: str,
    per_page: int = 100,
    page: int = 1,
    status: str = None,
    search: str = None,
    orderby: str = "date",
    order: str = "desc",
) -> dict:
    """Fetch posts from WordPress REST API with filtering and search.

    Args:
        project_id: Project ID to get WordPress site configuration
        per_page: Number of posts per page (default: 100, max 100)
        page: Page number (default: 1)
        status: Filter by post status (e.g., 'publish', 'draft', 'any')
        search: Search by post title/content
        orderby: Order by field (date, title, modified, etc.)
        order: ASC or DESC

    Returns:
        dict with 'posts' list and 'total' count
    """
    wp_site = await _get_wp_site(project_id)
    headers = _get_auth_header(wp_site["username"], wp_site["api_key"])

    url = f"{wp_site['url'].rstrip('/')}/wp-json/wp/v2/posts"
    params = {"per_page": per_page, "page": page, "_embed": True}
    if status:
        params["status"] = status
    if search:
        params["search"] = search
    if orderby:
        params["orderby"] = orderby
    if order:
        params["order"] = order

    result = await fetch_with_retry(url, headers, params)

    # Transform posts data for frontend consumption
    transformed_posts = []
    try:
        for post in result.get("posts", []):
            # Extract nested data from _embedded
            embedded = post.get("_embedded", {})
            categories = _extract_categories(embedded)
            tags = _extract_tags(embedded)

            # Format date and generate edit URL
            formatted_date = _format_date(post.get("date"))
            edit_url = _generate_edit_url(wp_site["url"], post.get("id"))

            # Add transformed fields to post (keep original fields intact)
            post["categories"] = categories
            post["tags"] = tags
            post["formatted_date"] = formatted_date
            post["edit_url"] = edit_url

            transformed_posts.append(post)
    except Exception as e:
        print(f"[TRANSFORM_ERROR] Failed to transform posts: {str(e)}")
        # Return original posts if transformation fails
        transformed_posts = result.get("posts", [])

    return {"posts": transformed_posts, "total": result.get("total", 0)}
