import pytest
from unittest.mock import call
from sqlalchemy.exc import SQLAlchemyError
from app.utils.exceptions import (
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
)
from app.models import User
from app.schemas.auth_schemas import (
    RegisterSchema,
    LoginSchema,
    DeactivateAccountSchema,
)

# Assuming your functions are in app.service.auth
from app.service.auth import (
    register,
    login,
    validate_email,
    validate_name,
    logout,
    reset_password,
    change_password,
    deactivate_account,
)


def create_user(
    email, username, password, first_name, last_name, is_active=True, user_id=1
):
    user = User(
        email=email,
        username=username,
        password=password,  # Updated to use 'password'
        first_name=first_name,
        last_name=last_name,
    )
    user.is_active = is_active
    user.id = user_id
    return user


@pytest.fixture
def mock_db(mocker):
    return mocker.MagicMock()


@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("app.service.auth.logger")


@pytest.fixture
def mock_bcrypt(mocker):
    return mocker.patch("app.service.auth.bcrypt")


@pytest.fixture
def mock_generate_jwt(mocker):
    return mocker.patch("app.service.auth.generate_jwt")


@pytest.fixture
def mock_register_schema_load(mocker):
    return mocker.patch.object(RegisterSchema, "load")


@pytest.fixture
def mock_login_schema_load(mocker):
    return mocker.patch.object(LoginSchema, "load")


@pytest.fixture
def mock_deactivate_account_schema_load(mocker):
    return mocker.patch.object(DeactivateAccountSchema, "load")


# -------------------------
# Tests for register function
# -------------------------


def test_register_success(mock_db, mock_logger, mock_bcrypt, mock_register_schema_load) -> None:
    # Arrange
    email = "test@example.com"
    password = "Password123"
    first_name = "John"
    last_name = "Doe"
    username = "johndoe"

    mock_register_schema_load.return_value = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
    }

    mock_bcrypt.gensalt.return_value = b"salt"
    mock_bcrypt.hashpw.return_value = b"hashed_password"

    # Simulate no existing user
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Act
    response, status_code = register(
        email, password, first_name, last_name, username, db=mock_db
    )

    # Assert
    expected_calls = [
        call.info("Registering new user"),
        call.debug(f"User details: email={email}, username={username}"),
        call.info("Registration successful"),
    ]
    mock_logger.assert_has_calls(expected_calls, any_order=False)
    mock_db.query.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.add.assert_called_once()

    new_user = mock_db.add.call_args[0][0]
    assert new_user.email == email
    assert new_user.username == username
    assert (
        new_user.password == "hashed_password".decode("utf-8")
        if isinstance("hashed_password", bytes)
        else "hashed_password"
    )
    assert new_user.first_name == first_name
    assert new_user.last_name == last_name

    assert response == {
        "message": "Registration successful"
    }, "Unexpected registration response"
    assert status_code == 201, "Unexpected status code for registration"


def test_register_validation_error(mock_register_schema_load) -> None:
    # Arrange
    mock_register_schema_load.side_effect = ValidationError("Invalid data")

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        register("email", "password", "first", "last", "username", db=None)
    assert str(exc_info.value) == "Invalid data"


def test_register_existing_active_user(mock_db, mock_logger) -> None:
    # Arrange
    email = "test@example.com"
    username = "johndoe"
    password = "Password123"

    first_name = "John"
    last_name = "Doe"

    existing_user = create_user(
        email=email,
        username=username,
        password="hashed_password",
        first_name="Existing",
        last_name="User",
        is_active=True,
    )

    mock_db.query.return_value.filter.return_value.first.return_value = existing_user

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        register(email, password, first_name, last_name, username, db=mock_db)
    assert exc_info.value.message == {"message": "Email or username is already in use"}

    mock_logger.warning.assert_called_with("Email or username is already in use")


def test_register_database_error(
    mock_db, mock_logger, mock_bcrypt, mock_register_schema_load
) -> None:
    # Arrange
    email = "test@example.com"
    password = "Password123"
    first_name = "John"
    last_name = "Doe"
    username = "johndoe"

    mock_register_schema_load.return_value = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
    }

    mock_db.query.return_value.filter.return_value.first.return_value = None
    mock_bcrypt.gensalt.return_value = b"salt"
    mock_bcrypt.hashpw.return_value = b"hashed_password"
    mock_db.commit.side_effect = SQLAlchemyError("DB Error")

    # Act & Assert
    with pytest.raises(DatabaseError):
        register(email, password, first_name, last_name, username, db=mock_db)

    mock_logger.error.assert_called_with(
        "Database error during registration: DB Error", exc_info=True
    )
    mock_db.rollback.assert_called_once()


def test_register_reactivate_existing_inactive_user(
    mock_db, mock_logger, mock_bcrypt, mock_register_schema_load
) -> None:
    # Arrange
    email = "test@example.com"
    password = "NewPassword123"
    first_name = "Jane"
    last_name = "Doe"
    username = "johndoe"

    mock_register_schema_load.return_value = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
    }

    # Simulate existing inactive user
    existing_user = create_user(
        email=email,
        username=username,
        password="old_hashed_password",
        first_name="OldFirstName",
        last_name="OldLastName",
        is_active=False,
    )
    mock_db.query.return_value.filter.return_value.first.return_value = existing_user

    mock_bcrypt.gensalt.return_value = b"new_salt"
    mock_bcrypt.hashpw.return_value = b"new_hashed_password"

    # Act
    response, status_code = register(
        email, password, first_name, last_name, username, db=mock_db
    )

    # Assert
    expected_calls = [
        call.info("Registering new user"),
        call.debug(f"User details: email={email}, username={username}"),
        call.info("Reactivating existing user"),
        call.info("Account reactivated successfully"),
    ]
    mock_logger.assert_has_calls(expected_calls, any_order=False)
    mock_db.query.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.add.assert_not_called()  # No new user should be added

    # Verify that the existing user's details were updated
    assert existing_user.password == "new_hashed_password"
    assert existing_user.first_name == first_name
    assert existing_user.last_name == last_name
    assert existing_user.username == username
    assert existing_user.is_active is True

    assert response == {
        "message": "Account reactivated successfully"
    }, "Unexpected response for reactivating existing inactive user"
    assert (
        status_code == 200
    ), "Unexpected status code for reactivating existing inactive user"


def test_register_unexpected_exception(
    mock_db, mock_logger, mock_bcrypt, mock_register_schema_load
) -> None:
    # Arrange
    email = "test@example.com"
    password = "Password123"
    first_name = "John"
    last_name = "Doe"
    username = "johndoe"

    mock_register_schema_load.return_value = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
    }

    # Simulate no existing user
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Simulate an unexpected exception during user creation
    mock_db.add.side_effect = Exception("Unexpected Error")

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        register(email, password, first_name, last_name, username, db=mock_db)

    assert str(exc_info.value) == "Unexpected Error"
    mock_logger.exception.assert_called_with("Error registering user: Unexpected Error")


# -------------------------
# Tests for login function
# -------------------------


def test_login_success(
    mock_db, mock_logger, mock_bcrypt, mock_generate_jwt, mock_login_schema_load
) -> None:
    # Arrange
    username = "johndoe"
    password = "Password123"
    hashed_password = "hashed_password"

    user = create_user(
        email="johndoe@example.com",
        username=username,
        password=hashed_password,
        first_name="John",
        last_name="Doe",
        is_active=True,
        user_id=1,
    )

    mock_login_schema_load.return_value = {
        "username": username,
        "password": password,
    }

    mock_db.query.return_value.filter_by.return_value.first.return_value = user
    mock_bcrypt.checkpw.return_value = True  # Simulate successful password check
    mock_generate_jwt.return_value = "mock_jwt_token"

    # Act
    response, status_code = login(username, password, db=mock_db)

    # Assert
    expected_calls = [
        call.info("Login attempt"),
        call.debug(f"Username: {username}"),
        call.info("Login successful"),
    ]
    mock_logger.assert_has_calls(expected_calls, any_order=False)
    mock_bcrypt.checkpw.assert_called_with(
        password.encode("utf-8"), hashed_password.encode("utf-8")
    )
    mock_generate_jwt.assert_called_with(user.id)

    assert response == {
        "message": "Login successful",
        "token": "mock_jwt_token",
    }, "Unexpected login response"
    assert status_code == 200, "Unexpected status code for login"


def test_login_validation_error(mock_login_schema_load) -> None:
    # Arrange
    mock_login_schema_load.side_effect = ValidationError("Invalid data")

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        login("username", "password", db=None)
    assert str(exc_info.value) == "Invalid data"


def test_login_invalid_username(mock_db, mock_logger, mock_login_schema_load) -> None:
    # Arrange
    username = "nonexistent"
    password = "Password123"

    mock_login_schema_load.return_value = {
        "username": username,
        "password": password,
    }

    mock_db.query.return_value.filter_by.return_value.first.return_value = None

    # Act & Assert
    with pytest.raises(AuthenticationError) as exc_info:
        login(username, password, db=mock_db)
    assert str(exc_info.value) == "Invalid username or password"

    mock_logger.warning.assert_called_with("Invalid username or password")


def test_login_inactive_user(mock_db, mock_logger, mock_login_schema_load) -> None:
    # Arrange
    username = "johndoe"
    password = "Password123"
    hashed_password = "hashed_password"

    user = create_user(
        email="johndoe@example.com",
        username=username,
        password=hashed_password,
        first_name="John",
        last_name="Doe",
        is_active=False,
    )

    mock_login_schema_load.return_value = {
        "username": username,
        "password": password,
    }

    mock_db.query.return_value.filter_by.return_value.first.return_value = user

    # Act & Assert
    with pytest.raises(AuthorizationError) as exc_info:
        login(username, password, db=mock_db)
    assert str(exc_info.value) == "User account is inactive"

    mock_logger.warning.assert_called_with("User account is inactive")


def test_login_invalid_password(
    mock_db, mock_logger, mock_bcrypt, mock_login_schema_load
) -> None:
    # Arrange
    username = "johndoe"
    password = "WrongPassword"
    hashed_password = "hashed_password"

    user = create_user(
        email="johndoe@example.com",
        username=username,
        password=hashed_password,
        first_name="John",
        last_name="Doe",
        is_active=True,
    )

    mock_login_schema_load.return_value = {
        "username": username,
        "password": password,
    }

    mock_db.query.return_value.filter_by.return_value.first.return_value = user
    mock_bcrypt.checkpw.return_value = False  # Simulate failed password check

    # Act & Assert
    with pytest.raises(AuthenticationError) as exc_info:
        login(username, password, db=mock_db)
    assert str(exc_info.value) == "Invalid username or password"

    mock_logger.warning.assert_called_with("Invalid username or password")


def test_login_jwt_generation_failure(
    mock_db, mock_logger, mock_bcrypt, mock_generate_jwt, mock_login_schema_load
) -> None:
    # Arrange
    username = "johndoe"
    password = "Password123"
    hashed_password = "hashed_password"

    user = create_user(
        email="johndoe@example.com",
        username=username,
        password=hashed_password,
        first_name="John",
        last_name="Doe",
        is_active=True,
    )

    mock_login_schema_load.return_value = {
        "username": username,
        "password": password,
    }

    mock_db.query.return_value.filter_by.return_value.first.return_value = user
    mock_bcrypt.checkpw.return_value = True
    mock_generate_jwt.return_value = None  # Simulate JWT generation failure

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        login(username, password, db=mock_db)
    assert str(exc_info.value) == "JWT generation failed"

    mock_logger.error.assert_called_with("Failed to generate JWT")


def test_login_database_error(mock_db, mock_logger, mock_login_schema_load) -> None:
    # Arrange
    username = "johndoe"
    password = "Password123"

    mock_login_schema_load.return_value = {
        "username": username,
        "password": password,
    }

    mock_db.query.side_effect = SQLAlchemyError("DB Error")

    # Act & Assert
    with pytest.raises(DatabaseError):
        login(username, password, db=mock_db)

    mock_logger.error.assert_called_with(
        "Database error during login: DB Error", exc_info=True
    )
    mock_db.rollback.assert_called_once()


# -------------------------
# Tests for validate_email function
# -------------------------


def test_validate_email_valid() -> None:
    email = "test@example.com"
    result = validate_email(email)
    assert result is True, f"Expected True for valid email {email}"


def test_validate_email_invalid() -> None:
    email = "invalid-email"
    result = validate_email(email)
    assert result is False, f"Expected False for invalid email {email}"


def test_validate_email_edge_cases() -> None:
    # Valid emails
    valid_emails = [
        "user@example.com",
        "user.name+tag+sorting@example.com",
        "user_name@example.co.uk",
        "user-name@example.org",
    ]
    for email in valid_emails:
        assert validate_email(email) is True, f"Expected True for valid email {email}"

    # Invalid emails
    invalid_emails = [
        "plainaddress",
        "@missingusername.com",
        "username@.com",
        "username@com",
        "username@.com.com",
        ".username@yahoo.com",
        "username@yahoo.com.",
        "username@yahoo..com",
    ]
    for email in invalid_emails:
        assert (
            validate_email(email) is False
        ), f"Expected False for invalid email {email}"


# -------------------------
# Tests for validate_name function
# -------------------------


def test_validate_name_valid() -> None:
    name = "John"
    result = validate_name(name)
    assert result is True, f"Expected True for valid name {name}"


def test_validate_name_invalid() -> None:
    name = "John123"
    result = validate_name(name)
    assert result is False, f"Expected False for invalid name {name}"


def test_validate_name_edge_cases() -> None:
    # Valid names (only a-zA-Z as per regex)
    valid_names = ["John", "Alice", "Connor"]
    for name in valid_names:
        assert validate_name(name) is True, f"Expected True for valid name {name}"

    # Invalid names
    invalid_names = ["John123", "Alice!", "Bob_the_builder", "12345", " ", "Élodie"]
    for name in invalid_names:
        assert validate_name(name) is False, f"Expected False for invalid name {name}"


# -------------------------
# Tests for logout function
# -------------------------


def test_logout() -> None:
    response, status_code = logout()
    assert response == {"message": "Logout successful"}, "Unexpected logout response"
    assert status_code == 200, "Unexpected status code for logout"


# -------------------------
# Tests for reset_password function
# -------------------------


def test_reset_password() -> None:
    email = "test@example.com"
    response, status_code = reset_password(email)
    assert response == {
        "message": "Password reset link sent to email"
    }, "Unexpected reset password response"
    assert status_code == 200, "Unexpected status code for reset password"


# -------------------------
# Tests for change_password function
# -------------------------


def test_change_password_success(mock_logger) -> None:
    old_password = "password123"
    new_password = "newpassword456"

    # Act
    response, status_code = change_password(old_password, new_password)

    # Assert
    expected_calls = [
        call.info("Change password request received"),
        call.debug(f"Old password: {old_password}, New password: {new_password}"),
        call.info("Password changed successfully"),
    ]
    mock_logger.assert_has_calls(expected_calls, any_order=False)

    assert response == {
        "message": "Password changed successfully"
    }, "Unexpected change password response"
    assert status_code == 200, "Unexpected status code for change password"


def test_change_password_invalid_old_password(mock_logger) -> None:
    old_password = "wrongpassword"
    new_password = "newpassword456"

    # Act
    response, status_code = change_password(old_password, new_password)

    # Assert
    mock_logger.warning.assert_called_with("Invalid old password")
    assert response == {
        "message": "Invalid old password"
    }, "Unexpected response for invalid old password"
    assert status_code == 401, "Unexpected status code for invalid old password"


# -------------------------
# Tests for deactivate_account function
# -------------------------


def test_deactivate_account_success(
    mock_db, mock_logger, mock_deactivate_account_schema_load, mock_bcrypt
) -> None:
    # Arrange
    username = "johndoe"
    password = "Password123"

    mock_deactivate_account_schema_load.return_value = {
        "username": username,
        "password": password,
    }

    hashed_password = "hashed_password"

    user = create_user(
        email="johndoe@example.com",
        username=username,
        password=hashed_password,
        first_name="John",
        last_name="Doe",
        is_active=True,
    )

    mock_db.query.return_value.filter_by.return_value.first.return_value = user
    mock_bcrypt.checkpw.return_value = True  # Simulate successful password check

    # Act
    response, status_code = deactivate_account(username, password, db=mock_db)

    # Assert
    expected_calls = [
        call.info("Deactivate account request received"),
        call.debug(f"Username: {username}"),
        call.info("Account deactivated successfully"),
    ]
    mock_logger.assert_has_calls(expected_calls, any_order=False)
    mock_db.commit.assert_called_once()
    assert user.is_active is False, "User should be inactive after deactivation"
    assert response == {
        "message": "Account deactivated successfully"
    }, "Unexpected response for deactivation"
    assert status_code == 200, "Unexpected status code for deactivation"


def test_deactivate_account_invalid_credentials(
    mock_db, mock_logger, mock_deactivate_account_schema_load, mock_bcrypt
) -> None:
    # Arrange
    username = "johndoe"
    password = "WrongPassword"

    mock_deactivate_account_schema_load.return_value = {
        "username": username,
        "password": password,
    }

    hashed_password = "hashed_password"

    user = create_user(
        email="johndoe@example.com",
        username=username,
        password=hashed_password,
        first_name="John",
        last_name="Doe",
        is_active=True,
    )

    mock_db.query.return_value.filter_by.return_value.first.return_value = user
    mock_bcrypt.checkpw.return_value = False  # Simulate failed password check

    # Act
    response, status_code = deactivate_account(username, password, db=mock_db)

    # Assert
    mock_logger.warning.assert_called_with("Invalid username or password")
    assert response == {
        "error": "Invalid username or password"
    }, "Unexpected response for invalid credentials"
    assert status_code == 400, "Unexpected status code for invalid credentials"


def test_deactivate_account_user_not_found(
    mock_db, mock_logger, mock_deactivate_account_schema_load
) -> None:
    # Arrange
    username = "nonexistent"
    password = "Password123"

    mock_deactivate_account_schema_load.return_value = {
        "username": username,
        "password": password,
    }

    mock_db.query.return_value.filter_by.return_value.first.return_value = None

    # Act
    response, status_code = deactivate_account(username, password, db=mock_db)

    # Assert
    mock_logger.warning.assert_called_with("Invalid username or password")
    assert response == {
        "error": "Invalid username or password"
    }, "Unexpected response for user not found"
    assert status_code == 400, "Unexpected status code for user not found"


def test_deactivate_account_already_inactive(
    mock_db, mock_logger, mock_deactivate_account_schema_load
) -> None:
    # Arrange
    username = "johndoe"
    password = "Password123"

    mock_deactivate_account_schema_load.return_value = {
        "username": username,
        "password": password,
    }

    # Simulate existing inactive user
    existing_user = create_user(
        email="johndoe@example.com",
        username=username,
        password="hashed_password",
        first_name="John",
        last_name="Doe",
        is_active=False,  # User is already inactive
    )
    mock_db.query.return_value.filter_by.return_value.first.return_value = existing_user

    # Act
    response, status_code = deactivate_account(username, password, db=mock_db)

    # Assert
    expected_calls = [
        call.info("Deactivate account request received"),
        call.debug(f"Username: {username}"),
        call.warning("User account is already inactive"),
    ]
    mock_logger.assert_has_calls(expected_calls, any_order=False)
    mock_db.commit.assert_not_called()  # No commit should occur
    assert response == {
        "error": "User account is already inactive"
    }, "Unexpected response for already inactive user"
    assert status_code == 400, "Unexpected status code for already inactive user"


def test_deactivate_account_schema_validation_error(
    mock_deactivate_account_schema_load,
) -> None:
    # Arrange
    mock_deactivate_account_schema_load.side_effect = ValidationError("Invalid data")

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        deactivate_account("username", "password", db=None)
    assert str(exc_info.value) == "Invalid data"


def test_deactivate_account_exception(
    mock_db, mock_logger, mock_deactivate_account_schema_load
) -> None:
    # Arrange
    username = "johndoe"
    password = "Password123"

    mock_deactivate_account_schema_load.return_value = {
        "username": username,
        "password": password,
    }

    mock_db.query.side_effect = Exception("Unexpected Error")

    # Act
    response, status_code = deactivate_account(username, password, db=mock_db)

    # Assert
    mock_logger.error.assert_called_with(
        "Error deactivating account: Unexpected Error", exc_info=True
    )
    assert response == {
        "message": "Internal server error"
    }, "Unexpected response for exception"
    assert status_code == 500, "Unexpected status code for exception"


# -------------------------
# Additional Tests for Edge Cases
# -------------------------


def test_register_with_missing_arguments(
    mock_db, mock_logger, mock_bcrypt, mock_register_schema_load
) -> None:
    # Arrange
    # Missing last_name
    mock_register_schema_load.side_effect = ValidationError("Missing data")

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        register("email", "password", "first", None, "username", db=mock_db)
    assert str(exc_info.value) == "Missing data"


def test_login_with_empty_password(mock_login_schema_load) -> None:
    # Arrange
    mock_login_schema_load.side_effect = ValidationError("Password cannot be empty")

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        login("username", "", db=None)
    assert str(exc_info.value) == "Password cannot be empty"


def test_deactivate_account_with_empty_username(mock_deactivate_account_schema_load) -> None:
    # Arrange
    mock_deactivate_account_schema_load.side_effect = ValidationError(
        "Username cannot be empty"
    )

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        deactivate_account("", "password", db=None)
    assert str(exc_info.value) == "Username cannot be empty"


# -------------------------
# Tests for validate_email and validate_name regex paths
# -------------------------


# def test_validate_email_edge_cases():
#     # Valid emails
#     valid_emails = [
#         "user@example.com",
#         "user.name+tag+sorting@example.com",
#         "user_name@example.co.uk",
#         "user-name@example.org",
#     ]
#     for email in valid_emails:
#         assert validate_email(email) is True, f"Expected True for valid email {email}"

#     # Invalid emails
#     invalid_emails = [
#         "plainaddress",
#         "@missingusername.com",
#         "username@.com",
#         "username@com",
#         "username@.com.com",
#         ".username@yahoo.com",
#         "username@yahoo.com.",
#         "username@yahoo..com",
#     ]
#     for email in invalid_emails:
#         assert (
#             validate_email(email) is False
#         ), f"Expected False for invalid email {email}"


def test_validate_email_leading_dot() -> None:
    # Invalid email with leading dot in local part
    email = ".username@yahoo.com"
    result = validate_email(email)
    assert result is False, f"Expected False for invalid email {email}"


def test_validate_email_trailing_dot() -> None:
    # Invalid email with trailing dot in domain
    email = "username@yahoo.com."
    result = validate_email(email)
    assert result is False, f"Expected False for invalid email {email}"


def test_validate_email_consecutive_dots() -> None:
    # Invalid email with consecutive dots in local part
    email = "user..name@example.com"
    result = validate_email(email)
    assert result is False, f"Expected False for invalid email {email}"


def test_validate_email_valid_subdomains() -> None:
    # Valid email with multiple subdomains
    email = "user@sub.mail.example.com"
    result = validate_email(email)
    assert result is True, f"Expected True for valid email {email}"


# def test_validate_name_edge_cases():
#     # Valid names (only a-zA-Z as per regex)
#     valid_names = ["John", "Alice", "Connor"]
#     for name in valid_names:
#         assert validate_name(name) is True, f"Expected True for valid name {name}"

#     # Invalid names
#     invalid_names = ["John123", "Alice!", "Bob_the_builder", "12345", " ", "Élodie"]
#     for name in invalid_names:
#         assert validate_name(name) is False, f"Expected False for invalid name {name}"
