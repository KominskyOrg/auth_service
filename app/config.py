import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


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
    logger.debug(f"FLASK_ENV: {env}")  # Replaced print with logger.debug

    if env == "local":
        config = LocalConfig
        logger.info("Loading LocalConfig")
    elif env == "development":
        config = DevConfig
        logger.info("Loading DevConfig")
    elif env == "production":
        config = ProdConfig
        logger.info("Loading ProdConfig")
    else:
        logger.error(f"Unknown environment: {env}")
        raise ValueError(f"Unknown environment: {env}")

    # Set log level based on environment
    if env == "production":
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)

    return config
