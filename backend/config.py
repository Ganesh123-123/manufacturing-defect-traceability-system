import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "manufacturing-defect-traceability-secret-key-2026")
    
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3307))
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DB = os.environ.get("MYSQL_DB", "defect_traceability")
    
    # Render provides PostgreSQL URLs without a driver name.
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if DATABASE_URL and DATABASE_URL.startswith(("postgres://", "postgresql://")):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

    # Allow explicit override via DATABASE_URL
    DEFAULT_MYSQL_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or DEFAULT_MYSQL_URL
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }
    
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
    EXPORT_DIR = os.environ.get("EXPORT_DIR", os.path.join(os.path.dirname(__file__), "exports"))

class TestConfig(Config):
    TESTING = True
    # Test can use in-memory SQLite or dedicated test DB
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")
    SQLALCHEMY_ENGINE_OPTIONS = {}
    EXPORT_DIR = os.environ.get("TEST_EXPORT_DIR", os.path.join(os.path.dirname(__file__), "..", ".pytest_cache", "test_exports"))
