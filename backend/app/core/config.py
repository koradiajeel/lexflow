from pydantic_settings import BaseSettings, SettingsConfigDict


class settings(BaseSettings):
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Websites allowed to call this API (comma-separated). On Render, add the Vercel address.
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:5174"

    
    # File storage: "local" (backend/uploads, the default) or "s3" (Amazon S3 bucket)
    STORAGE_BACKEND: str = "local"
    S3_BUCKET: str = ""
    AWS_REGION: str = "ap-south-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    
    # Email (SMTP). Empty SMTP_USER = email sending is switched off.
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    


settings = settings()

