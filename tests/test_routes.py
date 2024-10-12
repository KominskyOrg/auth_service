# tests/test_routes.py

import pytest
from flask import url_for
from unittest.mock import MagicMock
from sqlalchemy.exc import SQLAlchemyError

# Assuming your Flask app is created in app/__init__.py and named 'create_app'
from app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_handle_request(mocker):
    return mocker.patch("app.routes.handle_request")


@pytest.fixture
def mock_get_db(mocker):
    return mocker.patch("app.routes.get_db")


@pytest.fixture
def mock_auth_functions(mocker):
    return {
        "login": mocker.patch("app.routes.login"),
        "register": mocker.patch("app.routes.register"),
        "logout": mocker.patch("app.routes.logout"),
        "reset_password": mocker.patch("app.routes.reset_password"),
        "change_password": mocker.patch("app.routes.change_password"),
        "deactivate_account": mocker.patch("app.routes.deactivate_account"),
    }


# Helper function to simulate database context
def mock_db_context(mocker):
    mock_db = MagicMock()
    mocker.patch(
        "app.routes.get_db",
        return_value=MagicMock(
            __enter__=MagicMock(return_value=mock_db), __exit__=MagicMock()
        ),
    )
    return mock_db


# Tests for /login endpoint
@pytest.mark.parametrize(
    "data, expected_status, expected_response",
    [
        ({"username": "user1", "password": "pass1"}, 200, {"token": "abcd1234"}),
    ],
)
def test_login_success(
    client,
    mock_handle_request,
    mock_get_db,
    mock_auth_functions,
    mocker,
    data,
    expected_status,
    expected_response,
):
    mock_handle_request.return_value = (expected_response, expected_status)

    response = client.post("/service/auth/login", json=data)

    assert response.status_code == expected_status
    assert response.get_json() == expected_response
    mock_handle_request.assert_called_once_with(
        mock_auth_functions["login"], "user1", "pass1", db=mocker.ANY
    )


@pytest.mark.parametrize(
    "data, exception, error_response",
    [
        (
            {"username": "user1", "password": "pass1"},
            SQLAlchemyError("DB Error"),
            {"error": "Database error occurred"},
        ),
        (
            {"username": "user1", "password": "pass1"},
            Exception("Unexpected Error"),
            {"error": "An unexpected error occurred"},
        ),
    ],
)
def test_login_errors(
    client,
    mock_handle_request,
    mock_get_db,
    mock_auth_functions,
    mocker,
    data,
    exception,
    error_response,
):
    mock_handle_request.side_effect = exception

    response = client.post("/service/auth/login", json=data)

    if isinstance(exception, SQLAlchemyError):
        assert response.status_code == 500
        assert response.get_json() == {"error": "Database error occurred"}
    else:
        assert response.status_code == 500
        assert response.get_json() == {"error": "An unexpected error occurred"}
    mock_handle_request.assert_called_once_with(
        mock_auth_functions["login"], "user1", "pass1", db=mocker.ANY
    )


# Tests for /register endpoint
@pytest.mark.parametrize(
    "data, expected_status, expected_response",
    [
        (
            {
                "email": "user@example.com",
                "password": "pass1",
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
            },
            201,
            {"message": "User registered"},
        ),
    ],
)
def test_register_success(
    client,
    mock_handle_request,
    mock_get_db,
    mock_auth_functions,
    mocker,
    data,
    expected_status,
    expected_response,
):
    mock_handle_request.return_value = (expected_response, expected_status)

    response = client.post("/service/auth/register", json=data)

    assert response.status_code == expected_status
    assert response.get_json() == expected_response
    mock_handle_request.assert_called_once_with(
        mock_auth_functions["register"],
        "user@example.com",
        "pass1",
        "John",
        "Doe",
        "johndoe",
        db=mocker.ANY,
    )


@pytest.mark.parametrize(
    "data, exception, error_response",
    [
        (
            {
                "email": "user@example.com",
                "password": "pass1",
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
            },
            SQLAlchemyError("DB Error"),
            {"error": "Database error occurred"},
        ),
        (
            {
                "email": "user@example.com",
                "password": "pass1",
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
            },
            Exception("Unexpected Error"),
            {"error": "An unexpected error occurred"},
        ),
    ],
)
def test_register_errors(
    client,
    mock_handle_request,
    mock_get_db,
    mock_auth_functions,
    mocker,
    data,
    exception,
    error_response,
):
    mock_handle_request.side_effect = exception

    response = client.post("/service/auth/register", json=data)

    if isinstance(exception, SQLAlchemyError):
        assert response.status_code == 500
        assert response.get_json() == {"error": "Database error occurred"}
    else:
        assert response.status_code == 500
        assert response.get_json() == {"error": "An unexpected error occurred"}
    mock_handle_request.assert_called_once_with(
        mock_auth_functions["register"],
        "user@example.com",
        "pass1",
        "John",
        "Doe",
        "johndoe",
        db=mocker.ANY,
    )


# Tests for /logout endpoint
@pytest.mark.parametrize(
    "expected_status, expected_response",
    [
        (200, {"message": "Logged out"}),
    ],
)
def test_logout_success(
    client,
    mock_handle_request,
    mock_get_db,
    mock_auth_functions,
    mocker,
    expected_status,
    expected_response,
):
    mock_handle_request.return_value = (expected_response, expected_status)

    response = client.post("/service/auth/logout")

    assert response.status_code == expected_status
    assert response.get_json() == expected_response
    mock_handle_request.assert_called_once_with(
        mock_auth_functions["logout"], db=mocker.ANY
    )


@pytest.mark.parametrize(
    "exception, error_response",
    [
        (SQLAlchemyError("DB Error"), {"error": "Database error occurred"}),
        (Exception("Unexpected Error"), {"error": "An unexpected error occurred"}),
    ],
)
def test_logout_errors(
    client,
    mock_handle_request,
    mock_get_db,
    mock_auth_functions,
    mocker,
    exception,
    error_response,
):
    mock_handle_request.side_effect = exception

    response = client.post("/service/auth/logout")

    if isinstance(exception, SQLAlchemyError):
        assert response.status_code == 500
        assert response.get_json() == {"error": "Database error occurred"}
    else:
        assert response.status_code == 500
        assert response.get_json() == {"error": "An unexpected error occurred"}
    mock_handle_request.assert_called_once_with(
        mock_auth_functions["logout"], db=mocker.ANY
    )


# Tests for /reset-password endpoint
@pytest.mark.parametrize(
    "data, expected_status, expected_response",
    [
        ({"email": "user@example.com"}, 200, {"message": "Password reset email sent"}),
    ],
)
def test_reset_password_success(
    client,
    mock_handle_request,
    mock_get_db,
    mock_auth_functions,
    mocker,
    data,
    expected_status,
    expected_response,
):
    mock_handle_request.return_value = (expected_response, expected_status)

    response = client.post("/service/auth/reset-password", json=data)

    assert response.status_code == expected_status
    assert response.get_json() == expected_response
    mock_handle_request.assert_called_once_with(
        mock_auth_functions["reset_password"], "user@example.com", db=mocker.ANY
    )


@pytest.mark.parametrize(
    "data, exception, error_response",
    [
        (
            {"email": "user@example.com"},
            SQLAlchemyError("DB Error"),
            {"error": "Database error occurred"},
        ),
        (
            {"email": "user@example.com"},
            Exception("Unexpected Error"),
            {"error": "An unexpected error occurred"},
        ),
    ],
)
def test_reset_password_errors(
    client,
    mock_handle_request,
    mock_get_db,
    mock_auth_functions,
    mocker,
    data,
    exception,
    error_response,
):
    mock_handle_request.side_effect = exception

    response = client.post("/service/auth/reset-password", json=data)

    if isinstance(exception, SQLAlchemyError):
        assert response.status_code == 500
        assert response.get_json() == {"error": "Database error occurred"}
    else:
        assert response.status_code == 500
        assert response.get_json() == {"error": "An unexpected error occurred"}
    mock_handle_request.assert_called_once_with(
        mock_auth_functions["reset_password"], "user@example.com", db=mocker.ANY
    )


# Tests for /change-password endpoint
@pytest.mark.parametrize(
    "data, expected_status, expected_response",
    [
        (
            {"old_password": "oldpass", "new_password": "newpass"},
            200,
            {"message": "Password changed"},
        ),
    ],
)
def test_change_password_success(
    client,
    mock_handle_request,
    mock_get_db,
    mock_auth_functions,
    mocker,
    data,
    expected_status,
    expected_response,
):
    mock_handle_request.return_value = (expected_response, expected_status)

    response = client.post("/service/auth/change-password", json=data)

    assert response.status_code == expected_status
    assert response.get_json() == expected_response
    mock_handle_request.assert_called_once_with(
        mock_auth_functions["change_password"], "oldpass", "newpass", db=mocker.ANY
    )


@pytest.mark.parametrize(
    "data, exception, error_response",
    [
        (
            {"old_password": "oldpass", "new_password": "newpass"},
            SQLAlchemyError("DB Error"),
            {"error": "Database error occurred"},
        ),
        (
            {"old_password": "oldpass", "new_password": "newpass"},
            Exception("Unexpected Error"),
            {"error": "An unexpected error occurred"},
        ),
    ],
)
def test_change_password_errors(
    client,
    mock_handle_request,
    mock_get_db,
    mock_auth_functions,
    mocker,
    data,
    exception,
    error_response,
):
    mock_handle_request.side_effect = exception

    response = client.post("/service/auth/change-password", json=data)

    if isinstance(exception, SQLAlchemyError):
        assert response.status_code == 500
        assert response.get_json() == {"error": "Database error occurred"}
    else:
        assert response.status_code == 500
        assert response.get_json() == {"error": "An unexpected error occurred"}
    mock_handle_request.assert_called_once_with(
        mock_auth_functions["change_password"], "oldpass", "newpass", db=mocker.ANY
    )


# Tests for /deactivate-account endpoint
@pytest.mark.parametrize(
    "data, expected_status, expected_response",
    [
        (
            {"username": "user1", "password": "pass1"},
            200,
            {"message": "Account deactivated"},
        ),
    ],
)
def test_deactivate_account_success(
    client,
    mock_handle_request,
    mock_get_db,
    mock_auth_functions,
    mocker,
    data,
    expected_status,
    expected_response,
):
    mock_handle_request.return_value = (expected_response, expected_status)

    response = client.post("/service/auth/deactivate-account", json=data)

    assert response.status_code == expected_status
    assert response.get_json() == expected_response
    mock_handle_request.assert_called_once_with(
        mock_auth_functions["deactivate_account"], "user1", "pass1", db=mocker.ANY
    )


@pytest.mark.parametrize(
    "data, exception, error_response",
    [
        (
            {"username": "user1", "password": "pass1"},
            SQLAlchemyError("DB Error"),
            {"error": "Database error occurred"},
        ),
        (
            {"username": "user1", "password": "pass1"},
            Exception("Unexpected Error"),
            {"error": "An unexpected error occurred"},
        ),
    ],
)
def test_deactivate_account_errors(
    client,
    mock_handle_request,
    mock_get_db,
    mock_auth_functions,
    mocker,
    data,
    exception,
    error_response,
):
    mock_handle_request.side_effect = exception

    response = client.post("/service/auth/deactivate-account", json=data)

    if isinstance(exception, SQLAlchemyError):
        assert response.status_code == 500
        assert response.get_json() == {"error": "Database error occurred"}
    else:
        assert response.status_code == 500
        assert response.get_json() == {"error": "An unexpected error occurred"}
    mock_handle_request.assert_called_once_with(
        mock_auth_functions["deactivate_account"], "user1", "pass1", db=mocker.ANY
    )


# Tests for /health endpoint
def test_health(client):
    response = client.get("/service/auth/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "OK"}
