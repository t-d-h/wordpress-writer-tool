"""Tests for API endpoint integration with language field."""

import pytest
from bson import ObjectId


class TestPostLanguageAPI:
    """Tests for POST /api/posts with language field."""

    @pytest.mark.asyncio
    async def test_create_post_with_language(self, test_client, test_project):
        """POST /api/posts with language='vietnamese' returns 201 and stores language."""
        response = await test_client.post(
            "/api/posts",
            json={
                "project_id": test_project,
                "topic": "Test topic",
                "language": "vietnamese",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["language"] == "vietnamese"

    @pytest.mark.asyncio
    async def test_create_post_default_language(self, test_client, test_project):
        """POST /api/posts without language defaults to 'vietnamese'."""
        response = await test_client.post(
            "/api/posts", json={"project_id": test_project, "topic": "Test topic"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["language"] == "vietnamese"

    @pytest.mark.asyncio
    async def test_create_post_invalid_language_400(self, test_client, test_project):
        """POST /api/posts with invalid language returns 400."""
        response = await test_client.post(
            "/api/posts",
            json={
                "project_id": test_project,
                "topic": "Test topic",
                "language": "spanish",
            },
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_get_post_includes_language(
        self, test_client, test_project, mongodb_test_db
    ):
        """GET /api/posts/{id} returns language field."""
        # Create a post with language
        posts = mongodb_test_db["posts"]
        post_doc = {
            "project_id": test_project,
            "topic": "Test topic",
            "language": "vietnamese",
            "additional_requests": "",
            "ai_provider_id": None,
            "model_name": None,
            "auto_publish": False,
            "thumbnail_source": "ai",
            "thumbnail_provider_id": None,
            "thumbnail_model_name": None,
            "target_word_count": None,
            "target_section_count": None,
            "title": None,
            "meta_description": None,
            "outline": None,
            "sections": [],
            "content": None,
            "thumbnail_url": None,
            "status": "draft",
            "research_data": None,
            "research_done": False,
            "content_done": False,
            "thumbnail_done": False,
            "token_usage": {
                "research": 0,
                "outline": 0,
                "content": 0,
                "thumbnail": 0,
                "total": 0,
            },
            "jobs": [],
            "created_at": "2024-01-01T00:00:00Z",
            "wp_post_id": None,
            "wp_post_url": None,
        }
        result = await posts.insert_one(post_doc)
        post_id = str(result.inserted_id)

        # Get the post
        response = await test_client.get(f"/api/posts/{post_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "vietnamese"

    @pytest.mark.asyncio
    async def test_backward_compatibility_default(
        self, test_client, test_project, mongodb_test_db
    ):
        """GET /api/posts/{id} for post without language field returns 'english'."""
        # Create a post without language field (old data)
        posts = mongodb_test_db["posts"]
        post_doc = {
            "project_id": test_project,
            "topic": "Test topic",
            "additional_requests": "",
            "ai_provider_id": None,
            "model_name": None,
            "auto_publish": False,
            "thumbnail_source": "ai",
            "thumbnail_provider_id": None,
            "thumbnail_model_name": None,
            "target_word_count": None,
            "target_section_count": None,
            "title": None,
            "meta_description": None,
            "outline": None,
            "sections": [],
            "content": None,
            "thumbnail_url": None,
            "status": "draft",
            "research_data": None,
            "research_done": False,
            "content_done": False,
            "thumbnail_done": False,
            "token_usage": {
                "research": 0,
                "outline": 0,
                "content": 0,
                "thumbnail": 0,
                "total": 0,
            },
            "jobs": [],
            "created_at": "2024-01-01T00:00:00Z",
            "wp_post_id": None,
            "wp_post_url": None,
        }
        result = await posts.insert_one(post_doc)
        post_id = str(result.inserted_id)

        # Get the post
        response = await test_client.get(f"/api/posts/{post_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "english"

    @pytest.mark.asyncio
    async def test_list_posts_includes_language(
        self, test_client, test_project, mongodb_test_db
    ):
        """GET /api/posts/by-project/{project_id} returns language for each post."""
        # Create multiple posts with different languages
        posts = mongodb_test_db["posts"]
        post_docs = [
            {
                "project_id": test_project,
                "topic": f"Test topic {i}",
                "language": "vietnamese" if i % 2 == 0 else "english",
                "additional_requests": "",
                "ai_provider_id": None,
                "model_name": None,
                "auto_publish": False,
                "thumbnail_source": "ai",
                "thumbnail_provider_id": None,
                "thumbnail_model_name": None,
                "target_word_count": None,
                "target_section_count": None,
                "title": None,
                "meta_description": None,
                "outline": None,
                "sections": [],
                "content": None,
                "thumbnail_url": None,
                "status": "draft",
                "research_data": None,
                "research_done": False,
                "content_done": False,
                "thumbnail_done": False,
                "token_usage": {
                    "research": 0,
                    "outline": 0,
                    "content": 0,
                    "thumbnail": 0,
                    "total": 0,
                },
                "jobs": [],
                "created_at": "2024-01-01T00:00:00Z",
                "wp_post_id": None,
                "wp_post_url": None,
            }
            for i in range(3)
        ]
        await posts.insert_many(post_docs)

        # List posts
        response = await test_client.get(f"/api/posts/by-project/{test_project}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["posts"]) == 3
        for i, post in enumerate(data["posts"]):
            expected_language = "vietnamese" if i % 2 == 0 else "english"
            assert post["language"] == expected_language

    @pytest.mark.asyncio
    async def test_bulk_create_posts_with_language(self, test_client, test_project):
        """POST /api/posts/bulk with language applies to all posts."""
        response = await test_client.post(
            "/api/posts/bulk",
            json={
                "project_id": test_project,
                "topics": ["Topic 1", "Topic 2", "Topic 3"],
                "language": "english",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data) == 3
        for post in data:
            assert post["language"] == "english"
