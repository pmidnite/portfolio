import os
from dotenv import load_dotenv

# Load environment variables from .env file in the project root
load_dotenv()


class Config:
    # Flask/Secret Keys
    SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 3600))

    # API Auth credentials (replaces hardcoded values)
    API_USERNAME = os.environ.get("API_USERNAME")
    API_PASSWORD = os.environ.get("API_PASSWORD")

    # Database values
    DB_USERNAME = os.environ.get("DB_USERNAME")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_HOST = os.environ.get("DB_HOST")
    DB_NAME = os.environ.get("DB_NAME")

    # Database URI
    _uri = os.environ.get("SQLALCHEMY_DATABASE_URI")
    if _uri:
        SQLALCHEMY_DATABASE_URI = _uri
    elif all([DB_USERNAME, DB_PASSWORD, DB_HOST, DB_NAME]):
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    else:
        SQLALCHEMY_DATABASE_URI = None

    SQLALCHEMY_POOL_RECYCLE = int(os.environ.get("SQLALCHEMY_POOL_RECYCLE", 299))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": int(os.environ.get("SQLALCHEMY_POOL_RECYCLE", 299)),
        "pool_timeout": int(os.environ.get("SQLALCHEMY_POOL_TIMEOUT", 30)),
    }

    # Mail — MAIL_USE_TLS must be a bool, not a string
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_RECIPIENT = os.environ.get('MAIL_RECIPIENT')

    # Debug — never enable in production via hardcoded value
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
