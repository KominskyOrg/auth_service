# app/config.py

import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('app.config')


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    def __init__(self):
        logger.debug("Config base class initialized.")


class DevConfig(Config):
    def __init__(self):
        super().__init__()
        self.DEBUG = True
        self.ENV = "development"

        self.DB_USERNAME = os.getenv("DB_USERNAME", "auth_user")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD", "auth_password")
        self.DB_NAME = os.getenv("DB_NAME", "auth_database")
        self.DB_HOST = os.getenv("DB_HOST", "db")
        self.DB_PORT = os.getenv("DB_PORT", "3306")

        self.SQLALCHEMY_DATABASE_URI = (
            f"mysql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
        logger.debug("DevConfig initialized with DEBUG=True and ENV=development.")


class StagingConfig(Config):
    def __init__(self):
        super().__init__()
        self.DEBUG = True
        self.ENV = "staging"

        self.DB_USERNAME = os.getenv("DB_USERNAME")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")
        self.DB_NAME = os.getenv("DB_NAME")
        self.DB_HOST = os.getenv("DB_HOST")
        self.DB_PORT = os.getenv("DB_PORT")

        missing_vars = []
        for var_name, var_value in [
            ("DB_USERNAME", self.DB_USERNAME),
            ("DB_PASSWORD", self.DB_PASSWORD),
            ("DB_NAME", self.DB_NAME),
            ("DB_HOST", self.DB_HOST),
            ("DB_PORT", self.DB_PORT),
        ]:
            if not var_value:
                missing_vars.append(var_name)

        if missing_vars:
            logger.error(f"Missing environment variables for StagingConfig: {', '.join(missing_vars)}")
            raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")

        self.SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
        logger.debug("StagingConfig initialized with DEBUG=True and ENV=staging.")


class ProdConfig(Config):
    def __init__(self):
        super().__init__()
        self.DEBUG = False
        self.ENV = "production"

        self.DB_USERNAME = os.getenv("DB_USERNAME")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")
        self.DB_NAME = os.getenv("DB_NAME")
        self.DB_HOST = os.getenv("DB_HOST")
        self.DB_PORT = os.getenv("DB_PORT")

        missing_vars = []
        for var_name, var_value in [
            ("DB_USERNAME", self.DB_USERNAME),
            ("DB_PASSWORD", self.DB_PASSWORD),
            ("DB_NAME", self.DB_NAME),
            ("DB_HOST", self.DB_HOST),
            ("DB_PORT", self.DB_PORT),
        ]:
            if not var_value:
                missing_vars.append(var_name)

        if missing_vars:
            logger.error(f"Missing environment variables for ProdConfig: {', '.join(missing_vars)}")
            raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")

        self.SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
        logger.debug("ProdConfig initialized with DEBUG=False and ENV=production.")


def get_config():
    """
    Retrieves the appropriate configuration class based on the FLASK_ENV environment variable.
    Configures logging accordingly.
    """
    env = os.getenv("FLASK_ENV", "development")
    logger.debug(f"FLASK_ENV: {env}")

    if env == "development":
        config = DevConfig()
        logger.info("Loading DevConfig.")
    elif env == "staging":
        config = StagingConfig()
        logger.info("Loading StagingConfig.")
    elif env == "production":
        config = ProdConfig()
        logger.info("Loading ProdConfig.")
    else:
        logger.error(f"Unknown environment: {env}")
        raise ValueError(f"Unknown environment: {env}")

    # Set log level based on environment
    if env == "production":
        logger.setLevel(logging.INFO)
        logger.info("Log level set to INFO for production.")
    else:
        logger.setLevel(logging.DEBUG)
        logger.debug(f"Log level set to DEBUG for {env} environment.")

    return config
