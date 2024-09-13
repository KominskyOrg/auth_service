import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class LocalConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "LOCAL_DATABASE_URL", "mysql://auth_user:auth_password@db:3306/auth_database"
    )
    DEBUG = True
    ENV = "development"


class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DEV_DATABASE_URL",
        "mysql+pymysql://root:auth_password@localhost:3306/dev_database",
    )
    DEBUG = True
    ENV = "development"


class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "PROD_DATABASE_URL",
        "mysql+pymysql://root:auth_password@rds_endpoint:3306/prod_database",
    )
    DEBUG = False
    ENV = "production"


def get_config():
    env = os.getenv("FLASK_ENV", "local")
    if env == "local":
        return LocalConfig
    elif env == "development":
        return DevConfig
    elif env == "production":
        return ProdConfig
    else:
        raise ValueError(f"Unknown environment: {env}")
