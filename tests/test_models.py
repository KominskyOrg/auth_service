# tests/test_models.py

from app.models import User
from datetime import datetime
import logging

# -------------------- User Initialization Tests -------------------- #


def test_user_initialization(caplog) -> None:
    """Test the initialization of a User object.
    Ensures that all attributes are set correctly and logging occurs.
    """
    # Arrange
    email = "test@example.com"
    username = "testuser"
    password = "password"
    first_name = "Test"
    last_name = "User"

    # Set caplog to capture DEBUG and INFO levels for 'app.models' logger
    caplog.set_level(logging.DEBUG, logger="app.models")

    # Act
    user = User(
        email=email,
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )

    # Assert
    assert user.email == email
    assert user.username == username
    assert user.password == password
    assert user.first_name == first_name
    assert user.last_name == last_name
    assert user.is_active is True
    assert user.created_at is None  # Since created_at is set by the database

    # Verify logging calls
    assert f"Initializing User with username: {username}" in caplog.text
    assert f"User object created with username: {username}" in caplog.text


# -------------------- set_password Tests -------------------- #


def test_user_set_password(caplog) -> None:
    """Test the set_password method of the User class.
    Ensures that the password is updated and logging occurs.
    """
    # Arrange
    user = User(
        email="test@example.com",
        username="testuser",
        password="hashed_pw",
        first_name="Test",
        last_name="User",
    )
    new_password = "new_hashed_pw"

    # Set caplog to capture DEBUG and INFO levels for 'app.models' logger
    caplog.set_level(logging.DEBUG, logger="app.models")

    # Act
    user.set_password(new_password)

    # Assert
    assert user.password == new_password

    # Verify logging calls
    assert f"Setting new password for user: {user.username}" in caplog.text
    assert f"Password updated for user: {user.username}" in caplog.text


# -------------------- to_dict Tests -------------------- #


def test_user_to_dict_with_created_at(caplog) -> None:
    """Test the to_dict method of the User class when created_at is set.
    Ensures that the dictionary representation is correct and logging occurs.
    """
    # Arrange
    user = User(
        email="test@example.com",
        username="testuser",
        password="hashed_pw",
        first_name="Test",
        last_name="User",
    )
    user.id = 1  # Set a mock ID
    user.created_at = datetime(2023, 10, 1, 12, 0, 0)  # Simulate a creation time

    # Set caplog to capture DEBUG and INFO levels for 'app.models' logger
    caplog.set_level(logging.DEBUG, logger="app.models")

    # Act
    user_dict = user.to_dict()

    # Assert
    expected_dict = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
    }
    assert user_dict == expected_dict

    # Verify logging calls
    assert f"Converting User object to dictionary: {user.username}" in caplog.text


def test_user_to_dict_without_created_at(caplog) -> None:
    """Test the to_dict method of the User class when created_at is None.
    Ensures that the dictionary representation handles None correctly.
    """
    # Arrange
    user = User(
        email="test@example.com",
        username="testuser",
        password="hashed_pw",
        first_name="Test",
        last_name="User",
    )
    user.id = 1  # Set a mock ID
    user.created_at = None  # Simulate no creation time

    # Set caplog to capture DEBUG and INFO levels for 'app.models' logger
    caplog.set_level(logging.DEBUG, logger="app.models")

    # Act
    user_dict = user.to_dict()

    # Assert
    expected_dict = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "created_at": None,
    }
    assert user_dict == expected_dict

    # Verify logging calls
    assert f"Converting User object to dictionary: {user.username}" in caplog.text


# -------------------- Additional Tests for Coverage -------------------- #


def test_user_set_password_with_logging(caplog) -> None:
    """Ensures that set_password logs the appropriate messages."""
    # Arrange
    user = User(
        email="test@example.com",
        username="testuser",
        password="hashed_pw",
        first_name="Test",
        last_name="User",
    )
    new_password = "another_new_pw"

    # Set caplog to capture DEBUG and INFO levels for 'app.models' logger
    caplog.set_level(logging.DEBUG, logger="app.models")

    # Act
    user.set_password(new_password)

    # Assert
    assert user.password == new_password
    assert f"Setting new password for user: {user.username}" in caplog.text
    assert f"Password updated for user: {user.username}" in caplog.text


def test_user_initialization_logging(caplog) -> None:
    """Ensures that initializing a User object logs the appropriate messages."""
    # Arrange
    email = "another_test@example.com"
    username = "anotheruser"
    password = "another_hashed_pw"
    first_name = "Another"
    last_name = "User"

    # Set caplog to capture DEBUG and INFO levels for 'app.models' logger
    caplog.set_level(logging.DEBUG, logger="app.models")

    # Act
    User(
        email=email,
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )

    # Assert
    assert f"Initializing User with username: {username}" in caplog.text
    assert f"User object created with username: {username}" in caplog.text
