"""
config.py – Application configuration
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration shared by all environments."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")
    DEBUG = False
    TESTING = False

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Swagger / Flasgger
    SWAGGER = {
        "title": "Blog API",
        "version": "1.0.0",
        "description": "API REST pour gérer un blog simple – INF222 TAF1",
        "termsOfService": "",
        "uiversion": 3,
    }


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'blog_dev.db')}",
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///blog_prod.db")


# Map name → class
config_map = {
    "development": DevelopmentConfig,
    "testing":     TestingConfig,
    "production":  ProductionConfig,
}

# Active config (set APP_ENV env-var to switch)
active_config = config_map.get(os.environ.get("APP_ENV", "development"), DevelopmentConfig)
