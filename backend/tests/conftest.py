"""Test fixtures for pytest."""

import os
import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.main import app
from app.database import (
    posts_col,
    projects_col,
    jobs_col,
    ai_providers_col,
    wp_sites_col,
    default_models_col,
    wp_posts_cache_col,
)


@pytest.fixture(scope="session")
async def mongodb_test_db():
    """Async MongoDB test database fixture."""
    # Use test database name
    test_db_name = os.getenv("MONGODB_DB", "wordpress_writer_test")
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

    client = AsyncIOMotorClient(mongodb_url)
    db = client[test_db_name]

    yield db

    # Cleanup after all tests
    client.close()


@pytest.fixture(scope="function")
def test_client():
    """FastAPI test client using httpx.AsyncClient."""
    with TestClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="function")
async def test_project(mongodb_test_db):
    """Creates a test project in MongoDB for post tests."""
    projects = mongodb_test_db["projects"]

    project_data = {
        "name": "Test Project",
        "description": "Test project for testing",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }

    result = await projects.insert_one(project_data)
    project_id = str(result.inserted_id)

    yield project_id

    # Cleanup
    await projects.delete_one({"_id": result.inserted_id})


@pytest.fixture(scope="function")
async def cleanup_db(mongodb_test_db):
    """Cleanup fixture to drop test collections after each test."""
    yield

    # Drop all test collections
    collections = [
        "posts",
        "projects",
        "jobs",
        "ai_providers",
        "wp_sites",
        "default_models",
        "wp_posts_cache",
    ]

    for collection_name in collections:
        await mongodb_test_db[collection_name].delete_many({})
