import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:123456@localhost:5432/email_spam_classification"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MODEL_DIR = os.getenv("MODEL_DIR", "saved_models")
