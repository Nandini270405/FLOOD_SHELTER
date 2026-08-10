import os
from pathlib import Path

# Load environment variables from .env if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent


def _normalize_database_url(database_url: str | None) -> str | None:
    if not database_url:
        return None
    # Support older Heroku-style postgres URLs
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


class Config:
    # SECURITY: Use a strong secret key in production!
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        if os.getenv("FLASK_ENV") == "production":
            raise RuntimeError("SECRET_KEY environment variable is required in production!")
        SECRET_KEY = "dev-secret-key"

    DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "shelter.db"))
    DATABASE_URL = _normalize_database_url(os.getenv("DATABASE_URL"))
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or f"sqlite:///{Path(DB_PATH)}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "true").strip().lower() == "true"
    FLASK_RUN_HOST = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    FLASK_RUN_PORT = int(os.getenv("FLASK_RUN_PORT", "5000"))
    
    TEMPLATE_DIR = BASE_DIR / "templates"
    STATIC_DIR = BASE_DIR / "static"

    # Rate limiting configuration (if we add Flask-Limiter later)
    RATELIMIT_DEFAULT = "200 per day; 50 per hour"
    RATELIMIT_STORAGE_URL = "memory://"
