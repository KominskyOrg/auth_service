# tests/test_jwt.py

import pytest
from unittest.mock import patch, MagicMock
import importlib
import sys
import jwt
import logging

@pytest.fixture
def mock_load_dotenv():
    """
    Fixture to mock load_dotenv to prevent loading from .env file during tests.
    """
    with patch('app.jwt.load_dotenv'):
        yield

@pytest.fixture
def reload_jwt(mock_load_dotenv):
    """
    Fixture to reload the jwt module after setting environment variables.
    """
    def _reload(env_vars):
        with patch.dict("os.environ", env_vars, clear=True):
            # Remove 'app.jwt' from sys.modules to force re-import
            if "app.jwt" in sys.modules:
                del sys.modules["app.jwt"]
            # Import and reload the jwt module
            import app.jwt
            importlib.reload(app.jwt)
            return app.jwt
    return _reload

def test_generate_jwt_success(reload_jwt):
    """
    Test that generate_jwt returns a valid token when SECRET_KEY is set.
    """
    env_vars = {
        "SECRET_KEY": "test-secret-key",
    }
    jwt_module = reload_jwt(env_vars)
    token = jwt_module.generate_jwt("user123")
    
    assert token is not None
    # Decode the token to verify its contents
    decoded = jwt.decode(token, env_vars["SECRET_KEY"], algorithms=["HS256"])
    assert decoded["user_id"] == "user123"
    assert "exp" in decoded
    assert "iat" in decoded

def test_generate_jwt_default_secret_key(reload_jwt):
    """
    Test that generate_jwt uses the default SECRET_KEY when not set.
    """
    env_vars = {}
    jwt_module = reload_jwt(env_vars)
    token = jwt_module.generate_jwt("user123")
    
    assert token is not None
    # Decode using default secret key
    decoded = jwt.decode(token, "smile-secret-key", algorithms=["HS256"])
    assert decoded["user_id"] == "user123"
    assert "exp" in decoded
    assert "iat" in decoded

def test_generate_jwt_exception_handling(reload_jwt):
    """
    Test that generate_jwt returns None when an exception occurs.
    """
    env_vars = {
        "SECRET_KEY": "test-secret-key",
    }
    jwt_module = reload_jwt(env_vars)
    
    with patch('jwt.encode', side_effect=Exception("JWT encoding error")):
        token = jwt_module.generate_jwt("user123")
        assert token is None

def test_generate_jwt_logs_success(reload_jwt, caplog):
    """
    Test that generate_jwt logs the correct messages on success.
    """
    env_vars = {
        "SECRET_KEY": "test-secret-key",
    }
    jwt_module = reload_jwt(env_vars)
    
    with caplog.at_level(logging.DEBUG):
        token = jwt_module.generate_jwt("user123")
    
    assert "Generating JWT" in caplog.text
    assert "User ID: user123" in caplog.text
    assert "Generated JWT:" in caplog.text
    assert token is not None

def test_generate_jwt_logs_exception(reload_jwt, caplog):
    """
    Test that generate_jwt logs error when an exception occurs.
    """
    env_vars = {
        "SECRET_KEY": "test-secret-key",
    }
    jwt_module = reload_jwt(env_vars)
    
    with patch('jwt.encode', side_effect=Exception("JWT encoding error")), caplog.at_level(logging.ERROR):
        token = jwt_module.generate_jwt("user123")
    
    assert "Generating JWT" in caplog.text
    assert "User ID: user123" in caplog.text
    assert "Error generating JWT: JWT encoding error" in caplog.text
    assert token is None
