# tests/test_config.py

import pytest
from unittest.mock import patch
import logging
import importlib
import sys
from io import StringIO


@pytest.fixture
def import_config():
    """
    Fixture to set environment variables, configure logging, import the config module,
    and capture log outputs.
    """

    def _import_config(env_vars):
        # Create a StringIO stream to capture logs
        log_stream = StringIO()

        # Define a custom handler to capture logs
        test_handler = logging.StreamHandler(log_stream)
        test_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(levelname)s %(name)s:%(filename)s:%(lineno)d %(message)s"
        )
        test_handler.setFormatter(formatter)

        # Get the logger used in config.py
        logger = logging.getLogger("app.config")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(test_handler)

        # Patch environment variables
        with patch.dict("os.environ", env_vars, clear=True):
            # Remove 'app.config' from sys.modules to force re-import
            if "app.config" in sys.modules:
                del sys.modules["app.config"]
            # Import and reload the config module
            import app.config

            importlib.reload(app.config)

        # Capture log output
        handler = test_handler
        handler.flush()
        log_contents = log_stream.getvalue()
        logger.removeHandler(handler)

        return app.config, log_contents

    return _import_config


def test_base_config(import_config):
    """
    Test the base Config class.
    """
    env_vars = {}
    config_module, logs = import_config(env_vars)
    assert config_module.Config.SQLALCHEMY_TRACK_MODIFICATIONS is False
    assert "Config base class initialized." in logs


def test_dev_config_with_env(import_config):
    """
    Test DevConfig with LOCAL_DATABASE_URL set.
    """
    env_vars = {
        "FLASK_ENV": "development",
        "LOCAL_DATABASE_URL": "mysql://dev_user:dev_pass@localhost:3306/dev_db",
        "DB_USERNAME": "dev_user",
        "DB_PASSWORD": "dev_pass",
        "DB_NAME": "dev_db",
        "DB_HOST": "localhost",
        "DB_PORT": "3306",
    }
    config_module, logs = import_config(env_vars)
    # Instantiate DevConfig
    dev_config = config_module.DevConfig()
    assert (
        dev_config.SQLALCHEMY_DATABASE_URI
        == "mysql://dev_user:dev_pass@localhost:3306/dev_db"
    )
    assert dev_config.DEBUG is True
    assert dev_config.ENV == "development"
    assert "DevConfig initialized with DEBUG=True and ENV=development." in logs


def test_dev_config_without_env(import_config):
    """
    Test DevConfig without LOCAL_DATABASE_URL set, should use default.
    """
    env_vars = {
        "FLASK_ENV": "development",
        # No LOCAL_DATABASE_URL provided
        "DB_USERNAME": "auth_user",
        "DB_PASSWORD": "auth_password",
        "DB_NAME": "auth_database",
        "DB_HOST": "db",
        "DB_PORT": "3306",
    }
    config_module, logs = import_config(env_vars)
    # Instantiate DevConfig
    dev_config = config_module.DevConfig()
    assert (
        dev_config.SQLALCHEMY_DATABASE_URI
        == "mysql://auth_user:auth_password@db:3306/auth_database"
    )
    assert dev_config.DEBUG is True
    assert dev_config.ENV == "development"
    assert "DevConfig initialized with DEBUG=True and ENV=development." in logs


def test_staging_config(import_config):
    """
    Test StagingConfig with all required environment variables set.
    """
    env_vars = {
        "FLASK_ENV": "staging",
        "DB_USERNAME": "staging_user",
        "DB_PASSWORD": "staging_pass",
        "DB_NAME": "staging_db",
        "DB_HOST": "staging_host",
        "DB_PORT": "3307",
    }
    config_module, logs = import_config(env_vars)
    # Instantiate StagingConfig
    staging_config = config_module.StagingConfig()
    expected_uri = (
        "mysql+pymysql://staging_user:staging_pass@staging_host:3307/staging_db"
    )
    assert staging_config.SQLALCHEMY_DATABASE_URI == expected_uri
    assert staging_config.DEBUG is True
    assert staging_config.ENV == "staging"
    assert "StagingConfig initialized with DEBUG=True and ENV=staging." in logs


def test_staging_config_missing_env_vars(import_config):
    """
    Test StagingConfig with missing environment variables.
    Should raise EnvironmentError.
    """
    env_vars = {
        "FLASK_ENV": "staging",
        "DB_USERNAME": "staging_user",
        # Missing DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT
    }
    config_module, logs = import_config(env_vars)
    with pytest.raises(EnvironmentError) as excinfo:
        config_module.StagingConfig()
    assert (
        "Missing environment variables for StagingConfig: DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT"
        in str(excinfo.value)
    )
    assert (
        "Missing environment variables for StagingConfig: DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT"
        in logs
    )


def test_prod_config(import_config):
    """
    Test ProdConfig with all required environment variables set.
    """
    env_vars = {
        "FLASK_ENV": "production",
        "DB_USERNAME": "prod_user",
        "DB_PASSWORD": "prod_pass",
        "DB_NAME": "prod_db",
        "DB_HOST": "prod_host",
        "DB_PORT": "3308",
    }
    config_module, logs = import_config(env_vars)
    # Instantiate ProdConfig
    prod_config = config_module.ProdConfig()
    expected_uri = "mysql+pymysql://prod_user:prod_pass@prod_host:3308/prod_db"
    assert prod_config.SQLALCHEMY_DATABASE_URI == expected_uri
    assert prod_config.DEBUG is False
    assert prod_config.ENV == "production"
    assert "ProdConfig initialized with DEBUG=False and ENV=production." in logs


def test_prod_config_missing_env_vars(import_config):
    """
    Test ProdConfig with missing environment variables.
    Should raise EnvironmentError.
    """
    env_vars = {
        "FLASK_ENV": "production",
        "DB_USERNAME": "prod_user",
        "DB_PASSWORD": "prod_pass",
        # Missing DB_NAME, DB_HOST, DB_PORT
    }
    config_module, logs = import_config(env_vars)
    with pytest.raises(EnvironmentError) as excinfo:
        config_module.ProdConfig()
    assert (
        "Missing environment variables for ProdConfig: DB_NAME, DB_HOST, DB_PORT"
        in str(excinfo.value)
    )
    assert (
        "Missing environment variables for ProdConfig: DB_NAME, DB_HOST, DB_PORT"
        in logs
    )


def test_get_config_development(import_config):
    """
    Test get_config() returns DevConfig when FLASK_ENV is development.
    """
    env_vars = {
        "FLASK_ENV": "development",
        "LOCAL_DATABASE_URL": "mysql://dev_user:dev_pass@localhost:3306/dev_db",
        "DB_USERNAME": "dev_user",
        "DB_PASSWORD": "dev_pass",
        "DB_NAME": "dev_db",
        "DB_HOST": "localhost",
        "DB_PORT": "3306",
    }
    config_module, logs = import_config(env_vars)
    config_class = config_module.get_config()
    assert isinstance(config_class, config_module.DevConfig)
    assert "Loading DevConfig." in logs
    assert "Log level set to DEBUG for development environment." in logs


def test_get_config_staging(import_config):
    """
    Test get_config() returns StagingConfig when FLASK_ENV is staging.
    """
    env_vars = {
        "FLASK_ENV": "staging",
        "DB_USERNAME": "staging_user",
        "DB_PASSWORD": "staging_pass",
        "DB_NAME": "staging_db",
        "DB_HOST": "staging_host",
        "DB_PORT": "3307",
    }
    config_module, logs = import_config(env_vars)
    config_class = config_module.get_config()
    assert isinstance(config_class, config_module.StagingConfig)
    assert "Loading StagingConfig." in logs
    assert "Log level set to DEBUG for staging environment." in logs


def test_get_config_production(import_config):
    """
    Test get_config() returns ProdConfig when FLASK_ENV is production.
    """
    env_vars = {
        "FLASK_ENV": "production",
        "DB_USERNAME": "prod_user",
        "DB_PASSWORD": "prod_pass",
        "DB_NAME": "prod_db",
        "DB_HOST": "prod_host",
        "DB_PORT": "3308",
    }
    config_module, logs = import_config(env_vars)
    config_class = config_module.get_config()
    assert isinstance(config_class, config_module.ProdConfig)
    assert "Loading ProdConfig." in logs
    assert "Log level set to INFO for production." in logs


def test_get_config_unknown_env(import_config):
    """
    Test get_config() raises ValueError for unknown FLASK_ENV.
    """
    env_vars = {"FLASK_ENV": "unknown_env"}
    config_module, logs = import_config(env_vars)
    with pytest.raises(ValueError) as excinfo:
        config_module.get_config()
    assert "Unknown environment: unknown_env" in str(excinfo.value)
    assert "Unknown environment: unknown_env" in logs
