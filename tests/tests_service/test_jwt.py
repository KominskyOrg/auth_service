# tests/tests_service/test_jwt.py

import pytest
from unittest.mock import MagicMock
import jwt
import datetime
from app.service.jwt import generate_jwt, SECRET_KEY

def test_generate_jwt_success(mocker):
    user_id = 123
    mock_secret_key = "test-secret-key"
    mock_token = "mocked.jwt.token"

    # Patch the SECRET_KEY directly
    mocker.patch('app.service.jwt.SECRET_KEY', mock_secret_key)

    # Mock datetime.datetime to control the current time
    fixed_now = datetime.datetime(2024, 1, 1, 12, 0, 0)
    mock_datetime = mocker.patch('app.service.jwt.datetime')
    mock_datetime.datetime.now.return_value = fixed_now
    mock_datetime.timedelta = datetime.timedelta

    # Mock jwt.encode to return a predefined token
    mock_jwt_encode = mocker.patch('app.service.jwt.jwt.encode', return_value=mock_token)

    # Mock the logger
    mock_logger = mocker.patch('app.service.jwt.logger')

    token = generate_jwt(user_id)

    # Assertions
    assert token == mock_token, "The generated token should match the mocked token."
    mock_logger.info.assert_called_once_with("Generating JWT")
    mock_logger.debug.assert_any_call(f"User ID: {user_id}")
    mock_jwt_encode.assert_called_once()

    # Verify the payload passed to jwt.encode
    expected_payload = {
        "user_id": user_id,
        "exp": fixed_now + datetime.timedelta(hours=1),
        "iat": fixed_now,
    }
    mock_jwt_encode.assert_called_with(expected_payload, mock_secret_key, algorithm="HS256")
    mock_logger.debug.assert_called_with(f"Generated JWT: {mock_token}")

def test_generate_jwt_exception(mocker):
    user_id = 123

    # Patch the SECRET_KEY directly
    mocker.patch('app.service.jwt.SECRET_KEY', "test-secret-key")

    # Mock jwt.encode to raise an exception
    mock_jwt_encode = mocker.patch('app.service.jwt.jwt.encode', side_effect=Exception("JWT encoding failed"))

    # Mock the logger
    mock_logger = mocker.patch('app.service.jwt.logger')

    token = generate_jwt(user_id)

    # Assertions
    assert token is None, "The token should be None when an exception occurs."
    mock_logger.info.assert_called_once_with("Generating JWT")
    mock_logger.debug.assert_any_call(f"User ID: {user_id}")
    mock_jwt_encode.assert_called_once()
    mock_logger.error.assert_called_once()
    error_call_args = mock_logger.error.call_args
    assert "Error generating JWT: JWT encoding failed" in str(error_call_args), "Error message should be logged correctly."

def test_generate_jwt_default_secret_key(mocker):
    user_id = 456
    mock_token = "default-secret.jwt.token"

    # Patch the SECRET_KEY to return the default by not setting it
    mocker.patch('app.service.jwt.SECRET_KEY', "smile-secret-key")

    # Mock datetime.datetime to control the current time
    fixed_now = datetime.datetime(2024, 1, 1, 12, 0, 0)
    mock_datetime = mocker.patch('app.service.jwt.datetime')
    mock_datetime.datetime.now.return_value = fixed_now
    mock_datetime.timedelta = datetime.timedelta

    # Mock jwt.encode to return a predefined token
    mock_jwt_encode = mocker.patch('app.service.jwt.jwt.encode', return_value=mock_token)

    # Mock the logger
    mock_logger = mocker.patch('app.service.jwt.logger')

    token = generate_jwt(user_id)

    # Assertions
    assert token == mock_token, "The generated token should match the mocked token."
    mock_logger.info.assert_called_once_with("Generating JWT")
    mock_logger.debug.assert_any_call(f"User ID: {user_id}")
    mock_jwt_encode.assert_called_once()

    # Verify the payload passed to jwt.encode
    expected_payload = {
        "user_id": user_id,
        "exp": fixed_now + datetime.timedelta(hours=1),
        "iat": fixed_now,
    }
    mock_jwt_encode.assert_called_with(expected_payload, "smile-secret-key", algorithm="HS256")
    mock_logger.debug.assert_called_with(f"Generated JWT: {mock_token}")
