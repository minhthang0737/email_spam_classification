import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:123456@localhost:5432/email_spam_classification",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MODEL_DIR = os.getenv("MODEL_DIR", str(BASE_DIR / "saved_models"))
    TESTING = False


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    MODEL_DIR = tempfile.mkdtemp(prefix="spam_model_test_")
