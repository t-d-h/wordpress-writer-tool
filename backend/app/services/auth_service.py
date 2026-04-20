from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.hash import argon2
from bson import ObjectId
from app.config import settings
from app.database import users_col
from app.redis_client import redis_client
import json


class ObjectIdEncoder(json.JSONEncoder):
    """Custom JSON encoder for MongoDB ObjectId."""

    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)


# Configure Argon2id with balanced parameters
password_hasher = argon2.using(
    type="id", time_cost=3, memory_cost=128000, parallelism=2, salt_size=16, hash_len=32
)

ALGORITHM = "HS256"
ISSUER = "wordpress-writer"
AUDIENCE = "wordpress-writer-api"


def hash_password(password: str) -> str:
    """Hash password using Argon2id."""
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash (constant-time)."""
    return password_hasher.verify(plain_password, hashed_password)


def create_access_token(user_id: str, username: str, role: str) -> str:
    """Create JWT access token with custom claims."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": username,
        "user_id": user_id,
        "username": username,
        "role": role,
        "iss": ISSUER,
        "aud": AUDIENCE,
        "exp": expire,
        "iat": now,
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: str, username: str) -> str:
    """Create JWT refresh token with 30-day expiration."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=30)

    payload = {
        "sub": username,
        "user_id": user_id,
        "username": username,
        "iss": ISSUER,
        "aud": AUDIENCE,
        "exp": expire,
        "iat": now,
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=ISSUER,
            audience=AUDIENCE,
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired, please login again")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token, please login again")


async def get_user(username: str) -> Optional[dict]:
    """Get user from MongoDB or Redis cache."""
    cache_key = f"auth:user:{username}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    user = await users_col.find_one({"username": username})
    if user:
        user["id"] = str(user["_id"])
        del user["_id"]
        await redis_client.set(cache_key, json.dumps(user, cls=ObjectIdEncoder), ex=900)
    return user


async def get_user_by_id(user_id: str) -> Optional[dict]:
    """Get user by ID from MongoDB or Redis cache."""
    cache_key = f"auth:user:{user_id}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    user = await users_col.find_one({"_id": ObjectId(user_id)})
    if user:
        user["id"] = str(user["_id"])
        del user["_id"]
        await redis_client.set(cache_key, json.dumps(user, cls=ObjectIdEncoder), ex=900)
    return user


async def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user with username and password."""
    user = await get_user(username)
    if not user:
        # Verify against dummy hash to prevent timing attacks
        DUMMY_HASH = password_hasher.hash("dummypassword")
        password_hasher.verify(password, DUMMY_HASH)
        return None

    if not verify_password(password, user["password_hash"]):
        return None

    return user
