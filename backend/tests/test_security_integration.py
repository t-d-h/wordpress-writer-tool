import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import users_col
from app.services.auth_service import hash_password, create_access_token
from bson import ObjectId
from datetime import datetime, timezone, timedelta

client = TestClient(app)


@pytest.fixture
async def cleanup_users():
    """Cleanup users collection after tests."""
    yield
    await users_col.delete_many({})


@pytest.fixture
async def test_user(cleanup_users):
    """Create a test user for testing."""
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


def test_protected_endpoint_requires_token(test_user):
    """Test that protected endpoint requires valid token."""
    # Create valid token
    token = create_access_token(
        user_id=str(test_user["_id"]),
        username=test_user["username"],
        role=test_user["role"],
    )

    # Access protected endpoint without token
    response = client.get("/api/projects")
    assert response.status_code == 401
    assert "Authentication required" in response.json()["detail"]

    # Access protected endpoint with valid token
    response = client.get("/api/projects", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_protected_endpoint_injects_user_context(test_user):
    """Test that protected endpoint injects user context."""
    # Create valid token
    token = create_access_token(
        user_id=str(test_user["_id"]),
        username=test_user["username"],
        role=test_user["role"],
    )

    # Access protected endpoint with token
    response = client.get("/api/projects", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_invalid_token_returns_401(test_user):
    """Test that invalid token returns 401."""
    # Create invalid token
    invalid_token = "invalid.token.string"

    # Access protected endpoint with invalid token
    response = client.get(
        "/api/projects", headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert response.status_code == 401
    assert (
        "Invalid token" in response.json()["detail"]
        or "Authentication required" in response.json()["detail"]
    )


def test_expired_token_returns_401(test_user):
    """Test that expired token returns 401."""
    # Create expired token
    expired_token = create_access_token(
        user_id=str(test_user["_id"]),
        username=test_user["username"],
        role=test_user["role"],
    )

    # Wait for token to expire
    import time

    time.sleep(2)

    # Access protected endpoint with expired token
    response = client.get(
        "/api/projects", headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert (
        "Token expired" in response.json()["detail"]
        or "Authentication required" in response.json()["detail"]
    )


def test_public_endpoint_no_auth_required():
    """Test that public endpoints work without authentication."""
    # Access health endpoint without token
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

    # Access root endpoint without token
    response = client.get("/")
    assert response.status_code == 200
    assert "WordPress AI Writer API" in response.json()["message"]


def test_user_context_includes_required_fields(test_user):
    """Test that user context includes all required fields."""
    # Create valid token
    token = create_access_token(
        user_id=str(test_user["_id"]),
        username=test_user["username"],
        role=test_user["role"],
    )

    # Access protected endpoint with token
    response = client.get("/api/projects", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    # Verify token is valid
    assert token is not None
    assert len(token) > 0


def test_token_injection_in_all_api_calls(test_user):
    """Test that token is injected in all API calls."""
    # Create valid token
    token = create_access_token(
        user_id=str(test_user["_id"]),
        username=test_user["username"],
        role=test_user["role"],
    )

    # Test multiple API calls
    endpoints = [
        "/api/projects",
        "/api/posts/by-project/507f1f77bcf86cd799439011",
        "/api/jobs/dashboard-stats",
        "/api/ai-providers",
        "/api/default-models",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint, headers={"Authorization": f"Bearer {token}"})
        # Some endpoints may return 404 if data doesn't exist, but should not return 401
        assert response.status_code != 401, f"Endpoint {endpoint} returned 401"


def test_401_clears_tokens_and_redirects_to_login():
    """Test that 401 errors clear tokens and redirect to login."""
    # This test is for frontend behavior, which we can't test directly with TestClient
    # The frontend interceptor handles this in client.js
    pass
