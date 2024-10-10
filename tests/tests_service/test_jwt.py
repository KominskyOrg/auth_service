import pytest
import jwt
import datetime
from app.service.jwt import generate_jwt
from unittest.mock import patch, MagicMock

# Mock constants
SECRET_KEY = "smile-secret-key"


@patch("app.service.jwt.logger.debug")
@patch("app.service.jwt.jwt.encode")
def test_generate_jwt_success(mock_jwt_encode, mock_logger):
    # Setup mock values
    user_id = "test_user"
    mock_jwt_encode.return_value = "mock_token"
    now = datetime.datetime.now(datetime.UTC)

    # Call the function
    token = generate_jwt(user_id)

    # Assert the JWT encode is called with correct payload and secret key
    expected_payload = {
        "user_id": user_id,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1),
        "iat": datetime.datetime.now(datetime.UTC),
    }
    mock_jwt_encode.assert_called_once_with(
        expected_payload, SECRET_KEY, algorithm="HS256"
    )

    # Assert the token returned is correct
    assert token == "mock_token"

    # Assert logging calls
    mock_logger.info.assert_called_once_with("Generating JWT")
    mock_logger.debug.assert_any_call(f"User ID: {user_id}")
    mock_logger.debug.assert_any_call(f"Generated JWT: mock_token")


@patch("app.service.jwt.logger")
@patch("app.service.jwt.jwt.encode")
@patch("app.service.jwt.datetime")
def test_generate_jwt_exception(mock_datetime, mock_jwt_encode, mock_logger):
    # Setup mock values to trigger an exception
    user_id = "test_user"
    mock_datetime.datetime.now.side_effect = Exception("Datetime error")

    # Call the function
    token = generate_jwt(user_id)

    # Assert that the returned token is None due to the exception
    assert token is None

    # Assert logging calls
    mock_logger.info.assert_called_once_with("Generating JWT")
    mock_logger.error.assert_called_once()
    assert "Error generating JWT" in mock_logger.error.call_args[0][0]
