import pytest
from datetime import datetime, timezone
from unittest.mock import patch, AsyncMock
from bson import ObjectId
from app.services.user_service import create_admin_account
from app.database import users_col


@pytest.fixture
async def users_collection(mongodb_test_db):
    """Get users collection from test database."""
    return mongodb_test_db["users"]


async def test_admin_account_stored_with_correct_schema(users_collection):
    """Test that admin account is stored in users_col with correct schema (MONGO-01, MONGO-02)."""
    with (
        patch("app.services.user_service.settings") as mock_settings,
        patch("app.services.user_service.users_col", users_collection),
    ):
        mock_settings.INIT_USER = "test_admin"
        mock_settings.INIT_PASSWORD = "TestPassword123"

        await create_admin_account()

        # Verify admin account exists
        admin = await users_collection.find_one({"username": "test_admin"})
        assert admin is not None, "Admin account should be stored in users_col"

        # Verify schema fields
        assert "username" in admin, "Admin account should have username field"
        assert "password_hash" in admin, "Admin account should have password_hash field"
        assert "role" in admin, "Admin account should have role field"
        assert "created_at" in admin, "Admin account should have created_at field"
        assert "last_login_at" in admin, "Admin account should have last_login_at field"

        # Verify field values
        assert admin["username"] == "test_admin", "Username should match INIT_USER"
        assert admin["role"] == "admin", "Role should be admin"
        assert admin["password_hash"] is not None, "Password hash should be present"
        assert admin["password_hash"] != "", "Password hash should not be empty"
        assert admin["created_at"] is not None, "created_at should be present"
        assert admin["last_login_at"] is None, "last_login_at should be None initially"


async def test_unique_index_prevents_duplicate_usernames(users_collection):
    """Test that unique index on username prevents duplicate usernames (MONGO-03)."""
    with (
        patch("app.services.user_service.settings") as mock_settings,
        patch("app.services.user_service.users_col", users_collection),
    ):
        mock_settings.INIT_USER = "test_admin"
        mock_settings.INIT_PASSWORD = "TestPassword123"

        # Create admin account first time
        await create_admin_account()

        # Attempt to create admin account second time (should be idempotent)
        await create_admin_account()

        # Verify only one document exists
        count = await users_collection.count_documents({"username": "test_admin"})
        assert count == 1, (
            "Only one admin account should exist (unique index prevents duplicates)"
        )


async def test_admin_account_persists_across_restarts(users_collection):
    """Test that admin account persists across application restarts (idempotent behavior)."""
    with (
        patch("app.services.user_service.settings") as mock_settings,
        patch("app.services.user_service.users_col", users_collection),
    ):
        mock_settings.INIT_USER = "test_admin"
        mock_settings.INIT_PASSWORD = "TestPassword123"

        # Simulate first startup
        await create_admin_account()

        # Get initial admin account
        admin_before = await users_collection.find_one({"username": "test_admin"})
        admin_id = admin_before["_id"]

        # Simulate application restart (call create_admin_account again)
        await create_admin_account()

        # Verify admin account still exists with same ID
        admin_after = await users_collection.find_one({"username": "test_admin"})
        assert admin_after is not None, "Admin account should persist across restarts"
        assert admin_after["_id"] == admin_id, (
            "Admin account should have same ID (not duplicated)"
        )

        # Verify no duplicate accounts created
        count = await users_collection.count_documents({"username": "test_admin"})
        assert count == 1, "Only one admin account should exist after restart"
