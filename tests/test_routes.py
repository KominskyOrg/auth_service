# tests/test_auth_routes.py

import pytest
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
import logging

# Import the service functions to use in assertions
from app.service.auth import (
    login,
    register,
    logout,
    reset_password,
    change_password,
    deactivate_account,
)

# Import your Blueprint
from app.routes import auth_service_bp

# -------------------- Pytest Fixtures -------------------- #


@pytest.fixture(scope="module")
def app():
    """
    Fixture to create a Flask app with the auth_service_bp registered.
    """
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(auth_service_bp)
    # Configure app if necessary (e.g., app.config['TESTING'] = True)
    return app


# Note: pytest-flask provides the 'client' fixture, so you don't need to define it

# -------------------- Login Route Tests -------------------- #


def test_login_success(client, mocker, caplog):
    """
    Test the /login route for a successful login.
    Ensures that the response is correct and logging occurs.
    """
    # Arrange
    data = {"password": "testpass", "username": "testuser"}
    expected_response = {"message": "Login successful"}

    # Mock handle_request to return a successful response
    mock_handle_request = mocker.patch(
        "app.routes.handle_request",
        return_value=(expected_response, 200),  # Return raw data and status code
    )

    # Mock get_db context manager
    mock_get_db = mocker.patch("app.routes.get_db")

    # Set logging level to capture INFO and DEBUG logs
    caplog.set_level(logging.DEBUG, logger="app.routes")

    # Act
    response = client.post("/service/auth/login", json=data)

    # Assert
    assert response.status_code == 200
    assert response.get_json() == expected_response

    mock_handle_request.assert_called_once_with(
        login,
        data["username"],
        data["password"],
        db=mock_get_db().__enter__.return_value,
    )

    assert "Login request received" in caplog.text
    assert f"Request data: {data}" in caplog.text
    assert f"Response: ({expected_response}, 200)" in caplog.text


def test_login_db_error(client, mocker, caplog):
    """
    Test the /login route when a SQLAlchemyError occurs.
    Ensures that a 500 error is returned and logging occurs.
    """
    # Arrange
    data = {"password": "testpass", "username": "testuser"}

    # Mock handle_request to raise SQLAlchemyError
    mock_handle_request = mocker.patch(
        "app.routes.handle_request", side_effect=SQLAlchemyError("DB Error")
    )

    # Mock get_db context manager
    mock_get_db = mocker.patch("app.routes.get_db")

    # Set logging level to capture ERROR logs
    caplog.set_level(logging.ERROR, logger="app.routes")

    # Act
    response = client.post("/service/auth/login", json=data)

    # Assert
    assert response.status_code == 500
    assert response.get_json() == {"error": "Database error occurred"}

    mock_handle_request.assert_called_once_with(
        login,
        data["username"],
        data["password"],
        db=mock_get_db().__enter__.return_value,
    )

    assert "Database error during login: DB Error" in caplog.text


def test_login_unexpected_error(client, mocker, caplog):
    """
    Test the /login route when an unexpected Exception occurs.
    Ensures that a 500 error is returned and logging occurs.
    """
    # Arrange
    data = {"password": "testpass", "username": "testuser"}

    # Mock handle_request to raise a generic Exception
    mock_handle_request = mocker.patch(
        "app.routes.handle_request", side_effect=Exception("Unexpected Error")
    )

    # Mock get_db context manager
    mock_get_db = mocker.patch("app.routes.get_db")

    # Set logging level to capture ERROR logs
    caplog.set_level(logging.ERROR, logger="app.routes")

    # Act
    response = client.post("/service/auth/login", json=data)

    # Assert
    assert response.status_code == 500
    assert response.get_json() == {"error": "An unexpected error occurred"}

    mock_handle_request.assert_called_once_with(
        login,
        data["username"],
        data["password"],
        db=mock_get_db().__enter__.return_value,
    )

    assert "Unexpected error during login: Unexpected Error" in caplog.text


# -------------------- Register Route Tests -------------------- #


def test_register_success(client, mocker, caplog):
    """
    Test the /register route for a successful registration.
    Ensures that the response is correct and logging occurs.
    """
    # Arrange
    data = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "testpass",
        "username": "testuser",
    }
    expected_response = {"message": "Registration successful"}

    # Mock handle_request to return a successful response
    mock_handle_request = mocker.patch(
        "app.routes.handle_request",
        return_value=(expected_response, 201),  # Return raw data and status code
    )

    # Mock get_db context manager
    mock_get_db = mocker.patch("app.routes.get_db")

    # Set logging level to capture INFO and DEBUG logs
    caplog.set_level(logging.DEBUG, logger="app.routes")

    # Act
    response = client.post("/service/auth/register", json=data)

    # Assert
    assert response.status_code == 201
    assert response.get_json() == expected_response

    mock_handle_request.assert_called_once_with(
        register,
        data["email"],
        data["password"],
        data["first_name"],
        data["last_name"],
        data["username"],
        db=mock_get_db().__enter__.return_value,
    )

    assert "Register request received" in caplog.text
    assert f"Request data: {data}" in caplog.text
    assert f"Response: ({expected_response}, 201)" in caplog.text


# Continue rewriting the remaining tests in a similar fashion...

# -------------------- Logout Route Tests -------------------- #


def test_logout_success(client, mocker, caplog):
    """
    Test the /logout route for a successful logout.
    Ensures that the response is correct and logging occurs.
    """
    # Arrange
    expected_response = {"message": "Logout successful"}

    # Mock handle_request to return a successful response
    mock_handle_request = mocker.patch(
        "app.routes.handle_request", return_value=(expected_response, 200)
    )

    # Mock get_db context manager
    mock_get_db = mocker.patch("app.routes.get_db")

    # Set logging level to capture INFO and DEBUG logs
    caplog.set_level(logging.DEBUG, logger="app.routes")

    # Act
    response = client.post("/service/auth/logout")

    # Assert
    assert response.status_code == 200
    assert response.get_json() == expected_response

    mock_handle_request.assert_called_once_with(
        logout, db=mock_get_db().__enter__.return_value
    )

    assert "Logout request received" in caplog.text
    assert f"Response: ({expected_response}, 200)" in caplog.text


# -------------------- Reset Password Route Tests -------------------- #


def test_reset_password_success(client, mocker, caplog):
    """
    Test the /reset-password route for a successful password reset.
    Ensures that the response is correct and logging occurs.
    """
    # Arrange
    data = {"email": "test@example.com"}
    expected_response = {"message": "Password reset successful"}

    # Mock handle_request to return a successful response
    mock_handle_request = mocker.patch(
        "app.routes.handle_request", return_value=(expected_response, 200)
    )

    # Mock get_db context manager
    mock_get_db = mocker.patch("app.routes.get_db")

    # Set logging level to capture INFO and DEBUG logs
    caplog.set_level(logging.DEBUG, logger="app.routes")

    # Act
    response = client.post("/service/auth/reset-password", json=data)

    # Assert
    assert response.status_code == 200
    assert response.get_json() == expected_response

    mock_handle_request.assert_called_once_with(
        reset_password, data["email"], db=mock_get_db().__enter__.return_value
    )

    assert "Reset password request received" in caplog.text
    assert f"Request data: {data}" in caplog.text
    assert f"Response: ({expected_response}, 200)" in caplog.text


# -------------------- Change Password Route Tests -------------------- #


def test_change_password_success(client, mocker, caplog):
    """
    Test the /change-password route for a successful password change.
    Ensures that the response is correct and logging occurs.
    """
    # Arrange
    data = {"new_password": "newpass", "old_password": "oldpass"}
    expected_response = {"message": "Password change successful"}

    # Mock handle_request to return a successful response
    mock_handle_request = mocker.patch(
        "app.routes.handle_request", return_value=(expected_response, 200)
    )

    # Mock get_db context manager
    mock_get_db = mocker.patch("app.routes.get_db")

    # Set logging level to capture INFO and DEBUG logs
    caplog.set_level(logging.DEBUG, logger="app.routes")

    # Act
    response = client.post("/service/auth/change-password", json=data)

    # Assert
    assert response.status_code == 200
    assert response.get_json() == expected_response

    mock_handle_request.assert_called_once_with(
        change_password,
        data["old_password"],
        data["new_password"],
        db=mock_get_db().__enter__.return_value,
    )

    assert "Change password request received" in caplog.text
    assert f"Request data: {data}" in caplog.text
    assert f"Response: ({expected_response}, 200)" in caplog.text


# -------------------- Deactivate Account Route Tests -------------------- #


def test_deactivate_account_success(client, mocker, caplog):
    """
    Test the /deactivate-account route for a successful account deactivation.
    Ensures that the response is correct and logging occurs.
    """
    # Arrange
    data = {"password": "testpass", "username": "testuser"}
    expected_response = {"message": "Account deactivated successfully"}

    # Mock handle_request to return a successful response
    mock_handle_request = mocker.patch(
        "app.routes.handle_request", return_value=(expected_response, 200)
    )

    # Mock get_db context manager
    mock_get_db = mocker.patch("app.routes.get_db")

    # Set logging level to capture INFO and DEBUG logs
    caplog.set_level(logging.DEBUG, logger="app.routes")

    # Act
    response = client.post("/service/auth/deactivate-account", json=data)

    # Assert
    assert response.status_code == 200
    assert response.get_json() == expected_response

    mock_handle_request.assert_called_once_with(
        deactivate_account,
        data["username"],
        data["password"],
        db=mock_get_db().__enter__.return_value,
    )

    assert "Deactivate account request received" in caplog.text
    assert f"Request data: {data}" in caplog.text
    assert f"Response: ({expected_response}, 200)" in caplog.text


# -------------------- Health Route Test -------------------- #


def test_health_route(client, caplog):
    """
    Test the /health route to ensure it returns a healthy status.
    """
    # Arrange
    caplog.set_level(logging.INFO, logger="app.routes")

    # Act
    response = client.get("/service/auth/health")

    # Assert
    assert response.status_code == 200
    assert response.get_json() == {"status": "OK"}
    # Optionally verify logs if health route logs information


def test_health_route_no_logging(client, caplog):
    """
    Ensures that the /health route does not log any unexpected messages.
    """
    # Arrange
    caplog.set_level(logging.INFO, logger="app.routes")

    # Act
    response = client.get("/service/auth/health")

    # Assert
    assert response.status_code == 200
    assert response.get_json() == {"status": "OK"}

    # Ensure no error logs
    assert not any(record.levelno == logging.ERROR for record in caplog.records)
