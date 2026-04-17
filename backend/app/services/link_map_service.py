"""
Link Map Service — scans published WordPress posts for links and builds a link graph.
"""

import hashlib
from html.parser import HTMLParser
from urllib.parse import urlparse

from app.database import link_maps_col, projects_col, wp_sites_col
from app.services.wp_service import get_wp_posts, _get_wp_site, _get_auth_header, fetch_with_retry
from app.utils.time_utils import get_now
from bson import ObjectId


class LinkExtractor(HTMLParser):
    """Extract all href values from <a> tags in HTML content."""

    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr_name, attr_value in attrs:
                if attr_name == "href" and attr_value:
                    self.links.append(attr_value.strip())


def _extract_links_from_html(html_content: str) -> list[str]:
    """Parse HTML and return all href links."""
    if not html_content:
        return []
    parser = LinkExtractor()
    try:
        parser.feed(html_content)
    except Exception:
        return []
    return parser.links


def _is_internal_link(link: str, site_url: str) -> bool:
    """Check if a link points to the same WordPress site."""
    try:
        parsed_link = urlparse(link)
        parsed_site = urlparse(site_url)

        # Skip anchors, mailto, tel, javascript links
        if parsed_link.scheme in ("mailto", "tel", "javascript", ""):
            if not parsed_link.netloc and not link.startswith("/"):
                return False

        # Relative links are internal
        if not parsed_link.netloc:
            return True

        # Compare domains (strip www)
        link_domain = parsed_link.netloc.lower().replace("www.", "")
        site_domain = parsed_site.netloc.lower().replace("www.", "")
        return link_domain == site_domain
    except Exception:
        return False


def _normalize_url(url: str) -> str:
    """Normalize URL for comparison by removing trailing slash, query params, and fragments."""
    try:
        parsed = urlparse(url)
        path = parsed.path.rstrip("/")
        return f"{parsed.scheme}://{parsed.netloc}{path}".lower()
    except Exception:
        return url.lower().rstrip("/")


def _generate_external_id(url: str) -> str:
    """Generate a deterministic ID for an external URL."""
    domain = urlparse(url).netloc or url
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"ext_{url_hash}"


async def _fetch_all_published_posts(project_id: str) -> tuple[list, str]:
    """Fetch all published posts from WordPress, handling pagination.

    Returns:
        Tuple of (all_posts, site_url)
    """
    wp_site = await _get_wp_site(project_id)
    site_url = wp_site["url"].rstrip("/")

    all_posts = []
    page = 1
    per_page = 100
    max_pages = 5  # Safety limit: 500 posts max

    while page <= max_pages:
        result = await get_wp_posts(
            project_id,
            per_page=per_page,
            page=page,
            status="publish",
        )

        posts = result.get("posts", [])
        total = result.get("total", 0)

        all_posts.extend(posts)

        # Check if we've fetched all posts
        if len(all_posts) >= total or len(posts) < per_page:
            break

        page += 1

    return all_posts, site_url


async def scan_and_build_link_map(project_id: str) -> dict:
    """Scan all published posts for links and build the link map.

    Args:
        project_id: The project ID to scan

    Returns:
        The link map document that was saved to MongoDB
    """
    # Verify project exists
    project = await projects_col.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise Exception(f"Project {project_id} not found")

    print(f"[LINK_MAP] Starting link scan for project {project_id}")

    # Fetch all published posts
    all_posts, site_url = await _fetch_all_published_posts(project_id)
    print(f"[LINK_MAP] Fetched {len(all_posts)} published posts")

    if not all_posts:
        # Save empty link map
        link_map = {
            "project_id": project_id,
            "scanned_at": get_now(),
            "nodes": [],
            "edges": [],
            "stats": {
                "total_posts_scanned": 0,
                "total_internal_links": 0,
                "total_external_links": 0,
                "total_unique_external_domains": 0,
            },
        }
        await link_maps_col.update_one(
            {"project_id": project_id},
            {"$set": link_map},
            upsert=True,
        )
        return link_map

    # Build a URL -> post mapping for internal link resolution
    url_to_post = {}
    for post in all_posts:
        post_link = post.get("link", "")
        if post_link:
            normalized = _normalize_url(post_link)
            url_to_post[normalized] = {
                "id": post.get("id"),
                "title": post.get("title", {}).get("rendered", "")
                if isinstance(post.get("title"), dict)
                else post.get("title", "Untitled"),
                "url": post_link,
            }

    # Build nodes from posts
    nodes = []
    node_ids = set()
    for post in all_posts:
        post_id = post.get("id")
        title = (
            post.get("title", {}).get("rendered", "")
            if isinstance(post.get("title"), dict)
            else post.get("title", "Untitled")
        )
        nodes.append(
            {
                "id": str(post_id),
                "title": title,
                "url": post.get("link", ""),
                "type": "post",
            }
        )
        node_ids.add(str(post_id))

    # Extract links and build edges
    edges = []
    external_nodes = {}  # url -> node
    total_internal = 0
    total_external = 0
    external_domains = set()

    for post in all_posts:
        source_id = str(post.get("id"))
        content = (
            post.get("content", {}).get("rendered", "")
            if isinstance(post.get("content"), dict)
            else post.get("content", "")
        )

        links = _extract_links_from_html(content)

        for link in links:
            # Skip empty, anchor-only, or special protocol links
            if not link or link.startswith("#") or link.startswith("mailto:") or link.startswith("tel:") or link.startswith("javascript:"):
                continue

            if _is_internal_link(link, site_url):
                # Try to resolve to a known post
                normalized = _normalize_url(link)
                matched_post = url_to_post.get(normalized)

                if matched_post:
                    target_id = str(matched_post["id"])
                    # Skip self-links
                    if target_id != source_id:
                        edges.append(
                            {
                                "source": source_id,
                                "target": target_id,
                                "type": "internal",
                            }
                        )
                        total_internal += 1
                # If internal but doesn't match a known post, skip
                # (could be a page, category, etc.)
            else:
                # External link
                ext_id = _generate_external_id(link)
                if ext_id not in external_nodes:
                    parsed = urlparse(link)
                    domain = parsed.netloc or link
                    external_nodes[ext_id] = {
                        "id": ext_id,
                        "title": domain,
                        "url": link,
                        "type": "external",
                    }
                    external_domains.add(domain)

                edges.append(
                    {
                        "source": source_id,
                        "target": ext_id,
                        "type": "external",
                    }
                )
                total_external += 1

    # Add external nodes to the nodes list
    nodes.extend(external_nodes.values())

    # Build the link map document
    link_map = {
        "project_id": project_id,
        "scanned_at": get_now(),
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "total_posts_scanned": len(all_posts),
            "total_internal_links": total_internal,
            "total_external_links": total_external,
            "total_unique_external_domains": len(external_domains),
        },
    }

    # Upsert — one link map per project
    await link_maps_col.update_one(
        {"project_id": project_id},
        {"$set": link_map},
        upsert=True,
    )

    print(
        f"[LINK_MAP] Scan complete: {len(all_posts)} posts, "
        f"{total_internal} internal links, {total_external} external links, "
        f"{len(external_domains)} unique external domains"
    )

    return link_map


async def get_link_map(project_id: str) -> dict | None:
    """Get the latest link map for a project.

    Args:
        project_id: The project ID

    Returns:
        The link map document or None if not found
    """
    doc = await link_maps_col.find_one({"project_id": project_id})
    if doc:
        doc["id"] = str(doc.pop("_id"))
    return doc
