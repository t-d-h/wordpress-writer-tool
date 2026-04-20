import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.database import users_col
from app.services.auth_service import hash_password, create_access_token, decode_token
from bson import ObjectId

client = TestClient(app)


@pytest.fixture
async def cleanup_users():
    """Cleanup users collection after tests."""
    yield
    await users_col.delete_many({})


@pytest.fixture
async def test_user(cleanup_users):
    """Create a test user."""
    user_data = {
        "username": "testuser",
        "password_hash": hash_password("TestPass123"),
        "role": "user",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_login_at": None,
    }
    result = await users_col.insert_one(user_data)
    user_data["_id"] = result.inserted_id
    return user_data


def test_password_hashing():
    """Test password hashing with Argon2."""
    password = "TestPass123"
    hashed = hash_password(password)
    assert hashed != password
    assert len(hashed) > 50


def test_jwt_token_creation():
    """Test JWT token creation with required claims."""
    token = create_access_token(
        user_id=str(ObjectId()), username="testuser", role="user"
    )
    assert isinstance(token, str)
    assert len(token) > 50


def test_jwt_token_decode():
    """Test JWT token decoding and validation."""
    user_id = str(ObjectId())
    token = create_access_token(user_id=user_id, username="testuser", role="user")
    payload = decode_token(token)
    assert payload["user_id"] == user_id
    assert payload["username"] == "testuser"
    assert payload["role"] == "user"
    assert "exp" in payload
    assert "iat" in payload


def test_jwt_token_expiration():
    """Test JWT token expiration validation."""
    from app.services.auth_service import settings
    from app.config import Settings
    import jwt

    # Create token with short expiration
    now = datetime.now(timezone.utc)
    expire = now + timedelta(seconds=1)
    payload = {
        "sub": "testuser",
        "user_id": str(ObjectId()),
        "username": "testuser",
        "role": "user",
        "iss": "wordpress-writer",
        "aud": "wordpress-writer-api",
        "exp": expire,
        "iat": now,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    # Wait for token to expire
    import time

    time.sleep(2)

    # Should raise exception for expired token
    with pytest.raises(Exception, match="Token expired"):
        decode_token(token)


def test_login_success(test_user):
    """Test successful login."""
    response = client.post(
        "/api/auth/login", data={"username": "testuser", "password": "TestPass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    response = client.post(
        "/api/auth/login", data={"username": "testuser", "password": "WrongPass123"}
    )
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


def test_login_missing_user():
    """Test login with non-existent user."""
    response = client.post(
        "/api/auth/login", data={"username": "nonexistent", "password": "TestPass123"}
    )
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


def test_protected_endpoint_with_valid_token(test_user):
    """Test protected endpoint with valid token."""
    # Login to get token
    login_response = client.post(
        "/api/auth/login", data={"username": "testuser", "password": "TestPass123"}
    )
    token = login_response.json()["access_token"]

    # Access protected endpoint
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["role"] == "user"


def test_protected_endpoint_without_token():
    """Test protected endpoint without token."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert "Authentication required" in response.json()["detail"]


def test_protected_endpoint_with_invalid_token():
    """Test protected endpoint with invalid token."""
    response = client.get(
        "/api/auth/me", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]


def test_refresh_token_success(test_user):
    """Test refresh token endpoint."""
    # Login to get refresh token
    login_response = client.post(
        "/api/auth/login", data={"username": "testuser", "password": "TestPass123"}
    )
    refresh_token = login_response.json()["refresh_token"]

    # Refresh access token
    response = client.post("/api/auth/refresh", params={"refresh_token": refresh_token})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_refresh_token_invalid():
    """Test refresh token with invalid token."""
    response = client.post(
        "/api/auth/refresh", params={"refresh_token": "invalid_token"}
    )
    assert response.status_code == 401
    assert "Invalid refresh token" in response.json()["detail"]


def test_change_password_success(test_user):
    """Test successful password change."""
    # Login to get token
    login_response = client.post(
        "/api/auth/login", data={"username": "testuser", "password": "TestPass123"}
    )
    token = login_response.json()["access_token"]

    # Change password
    response = client.post(
        "/api/auth/change-password",
        json={"current_password": "TestPass123", "new_password": "NewPass456"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert "Password changed successfully" in response.json()["message"]

    # Verify new password works
    login_response = client.post(
        "/api/auth/login", data={"username": "testuser", "password": "NewPass456"}
    )
    assert login_response.status_code == 200


def test_change_password_wrong_current(test_user):
    """Test password change with wrong current password."""
    # Login to get token
    login_response = client.post(
        "/api/auth/login", data={"username": "testuser", "password": "TestPass123"}
    )
    token = login_response.json()["access_token"]

    # Try to change with wrong current password
    response = client.post(
        "/api/auth/change-password",
        json={"current_password": "WrongPass", "new_password": "NewPass456"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert "Current password is incorrect" in response.json()["detail"]


def test_change_password_without_token():
    """Test password change without authentication."""
    response = client.post(
        "/api/auth/change-password",
        json={"current_password": "TestPass123", "new_password": "NewPass456"},
    )
    assert response.status_code == 401
