import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.database import users_col
from app.services.user_service import (
    create_user,
    list_users,
    delete_user,
    reset_password,
    update_role,
)
from bson import ObjectId

client = TestClient(app)


@pytest.fixture
async def cleanup_users():
    """Cleanup users collection after tests."""
    yield
    await users_col.delete_many({})


@pytest.fixture
async def admin_user(cleanup_users):
    """Create an admin user for testing."""
    from app.services.auth_service import hash_password

    admin_data = {
        "username": "admin",
        "password_hash": hash_password("admin123"),
        "role": "admin",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_login_at": None,
    }
    result = await users_col.insert_one(admin_data)
    admin_data["_id"] = result.inserted_id
    return admin_data


@pytest.fixture
async def test_user(cleanup_users):
    """Create a test user."""
    user = await create_user("testuser", "TestPass123", "user")
    return user


def test_create_user(test_user):
    """Test creating a new user."""
    assert test_user["username"] == "testuser"
    assert test_user["role"] == "user"
    assert "password_hash" in test_user
    assert "created_at" in test_user


def test_create_user_duplicate_username(test_user):
    """Test creating user with duplicate username."""
    with pytest.raises(ValueError, match="Username already exists"):
        create_user("testuser", "AnotherPass123", "user")


def test_list_users(test_user):
    """Test listing all users."""
    users = await list_users()
    assert len(users) >= 1
    assert any(u["username"] == "testuser" for u in users)
    # Verify password_hash is excluded
    for user in users:
        assert "password_hash" not in user


def test_get_user(test_user):
    """Test getting user by ID."""
    user = await get_user(str(test_user["_id"]))
    assert user is not None
    assert user["username"] == "testuser"
    assert "password_hash" not in user


def test_delete_user(test_user):
    """Test deleting a user."""
    user_id = str(test_user["_id"])
    success = await delete_user(user_id)
    assert success is True

    # Verify user is deleted
    user = await get_user(user_id)
    assert user is None


def test_delete_nonexistent_user():
    """Test deleting a non-existent user."""
    fake_id = str(ObjectId())
    success = await delete_user(fake_id)
    assert success is False


def test_delete_admin_user(admin_user):
    """Test that admin account cannot be deleted."""
    with pytest.raises(ValueError, match="Cannot delete admin account"):
        await delete_user(str(admin_user["_id"]))


def test_reset_password(test_user):
    """Test resetting user password."""
    user_id = str(test_user["_id"])
    success = await reset_password(user_id, "NewPass456")
    assert success is True


def test_reset_password_nonexistent_user():
    """Test resetting password for non-existent user."""
    fake_id = str(ObjectId())
    success = await reset_password(fake_id, "NewPass456")
    assert success is False


def test_update_role(test_user):
    """Test updating user role."""
    user_id = str(test_user["_id"])
    success = await update_role(user_id, "editor")
    assert success is True

    # Verify role was updated
    user = await get_user(user_id)
    assert user["role"] == "editor"


def test_update_role_nonexistent_user():
    """Test updating role for non-existent user."""
    fake_id = str(ObjectId())
    success = await update_role(fake_id, "editor")
    assert success is False


def test_update_admin_role(admin_user):
    """Test that admin role cannot be changed."""
    with pytest.raises(ValueError, match="Cannot change admin role"):
        await update_role(str(admin_user["_id"]), "user")


def test_create_user_endpoint(test_user, admin_user):
    """Test user creation endpoint."""
    # Login as admin to get token
    from app.services.auth_service import create_access_token

    token = create_access_token(
        user_id=str(admin_user["_id"]),
        username=admin_user["username"],
        role=admin_user["role"],
    )

    response = client.post(
        "/api/users",
        json={"username": "newuser", "password": "NewPass123", "role": "user"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["role"] == "user"


def test_list_users_endpoint(test_user, admin_user):
    """Test user listing endpoint."""
    # Login as admin to get token
    from app.services.auth_service import create_access_token

    token = create_access_token(
        user_id=str(admin_user["_id"]),
        username=admin_user["username"],
        role=admin_user["role"],
    )

    response = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert len(data["users"]) >= 1


def test_delete_user_endpoint(test_user, admin_user):
    """Test user deletion endpoint."""
    user_id = str(test_user["_id"])

    # Login as admin to get token
    from app.services.auth_service import create_access_token

    token = create_access_token(
        user_id=str(admin_user["_id"]),
        username=admin_user["username"],
        role=admin_user["role"],
    )

    response = client.delete(
        f"/api/users/{user_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]


def test_reset_password_endpoint(test_user, admin_user):
    """Test password reset endpoint."""
    user_id = str(test_user["_id"])

    # Login as admin to get token
    from app.services.auth_service import create_access_token

    token = create_access_token(
        user_id=str(admin_user["_id"]),
        username=admin_user["username"],
        role=admin_user["role"],
    )

    response = client.post(
        f"/api/users/{user_id}/reset-password",
        json={"new_password": "NewPass456"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert "reset successfully" in response.json()["message"]


def test_update_role_endpoint(test_user, admin_user):
    """Test role update endpoint."""
    user_id = str(test_user["_id"])

    # Login as admin to get token
    from app.services.auth_service import create_access_token

    token = create_access_token(
        user_id=str(admin_user["_id"]),
        username=admin_user["username"],
        role=admin_user["role"],
    )

    response = client.put(
        f"/api/users/{user_id}/role",
        json={"role": "editor"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert "updated successfully" in response.json()["message"]
