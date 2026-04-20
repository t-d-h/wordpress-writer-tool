import os


class Settings:
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "wordpress_writer")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120")
    )
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    INIT_USER: str = os.getenv("INIT_USER")
    INIT_PASSWORD: str = os.getenv("INIT_PASSWORD")

    def validate(self) -> bool:
        """Validate that required configuration fields are present and non-empty."""
        if not self.INIT_USER:
            raise ValueError(
                "INIT_USER environment variable is required and cannot be empty"
            )
        if not self.INIT_PASSWORD:
            raise ValueError(
                "INIT_PASSWORD environment variable is required and cannot be empty"
            )
        return True


settings = Settings()
settings.validate()
