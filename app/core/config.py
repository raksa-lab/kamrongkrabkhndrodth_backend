from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://bookstore:bookstore@localhost:5432/bookstore"
    jwt_secret: str = "change-this-in-production"
    jwt_expire_minutes: int = 480
    upload_dir: str = "uploads"
    admin_email: str = "admin@example.com"
    admin_password: str = "change-me"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_bucket: str = "books"

    # MinIO / S3 Storage Settings
    minio_endpoint: str = ""
    minio_access_key: str = ""
    minio_secret_key: str = ""
    minio_bucket: str = "books"
    minio_secure: bool = True
    minio_public_url: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
