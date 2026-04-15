"""Tests for Pydantic model validation."""

import pytest
from pydantic import ValidationError

from app.models.post import PostCreate, BulkPostCreate


class TestPostCreateLanguage:
    """Tests for PostCreate language field validation."""

    def test_post_create_language_default(self):
        """Verify PostCreate defaults language to 'vietnamese'."""
        post = PostCreate(project_id="test-project-id", topic="Test topic")
        assert post.language == "vietnamese"

    def test_post_create_language_vietnamese(self):
        """Verify PostCreate accepts 'vietnamese'."""
        post = PostCreate(
            project_id="test-project-id", topic="Test topic", language="vietnamese"
        )
        assert post.language == "vietnamese"

    def test_post_create_language_english(self):
        """Verify PostCreate accepts 'english'."""
        post = PostCreate(
            project_id="test-project-id", topic="Test topic", language="english"
        )
        assert post.language == "english"

    def test_post_create_invalid_language_rejected(self):
        """Verify PostCreate rejects invalid language (e.g., 'spanish')."""
        with pytest.raises(ValidationError) as exc_info:
            PostCreate(
                project_id="test-project-id", topic="Test topic", language="spanish"
            )
        assert "language" in str(exc_info.value).lower()


class TestBulkPostCreateLanguage:
    """Tests for BulkPostCreate language field validation."""

    def test_bulk_post_create_language_default(self):
        """Verify BulkPostCreate defaults language to 'vietnamese'."""
        bulk_post = BulkPostCreate(
            project_id="test-project-id", topics=["Topic 1", "Topic 2"]
        )
        assert bulk_post.language == "vietnamese"

    def test_bulk_post_create_language_vietnamese(self):
        """Verify BulkPostCreate accepts 'vietnamese'."""
        bulk_post = BulkPostCreate(
            project_id="test-project-id",
            topics=["Topic 1", "Topic 2"],
            language="vietnamese",
        )
        assert bulk_post.language == "vietnamese"

    def test_bulk_post_create_language_english(self):
        """Verify BulkPostCreate accepts 'english'."""
        bulk_post = BulkPostCreate(
            project_id="test-project-id",
            topics=["Topic 1", "Topic 2"],
            language="english",
        )
        assert bulk_post.language == "english"

    def test_bulk_post_create_invalid_language_rejected(self):
        """Verify BulkPostCreate rejects invalid language."""
        with pytest.raises(ValidationError) as exc_info:
            BulkPostCreate(
                project_id="test-project-id",
                topics=["Topic 1", "Topic 2"],
                language="spanish",
            )
        assert "language" in str(exc_info.value).lower()
