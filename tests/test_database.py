import pytest
from unittest.mock import patch, MagicMock, ANY
from app.database import init_db, get_db, Base
from sqlalchemy.exc import SQLAlchemyError
import os
import sys

# -------------------- Mocking app.models -------------------- #

# Insert a mock for 'app.models' into sys.modules
# sys.modules['app.models'] = MagicMock()

# -------------------- init_db Tests -------------------- #


@patch("app.database.create_engine")
@patch("app.database.sessionmaker")
@patch("app.database.scoped_session")
@patch("app.database.Base.metadata.create_all")
def test_init_db_success(
    mock_create_all, mock_scoped_session, mock_sessionmaker, mock_create_engine
):
    # Mock the engine
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine

    # Mock the sessionmaker
    mock_SessionLocal = MagicMock()
    mock_sessionmaker.return_value = mock_SessionLocal

    # Mock the scoped_session
    mock_db_session = MagicMock()
    mock_scoped_session.return_value = mock_db_session

    # Call init_db without needing to mock imports
    init_db(app=None)  # 'app' parameter is not used in init_db

    # Assertions
    mock_create_engine.assert_called_once_with(
        os.getenv("DATABASE_URL", "sqlite:///./test.db"), pool_pre_ping=True
    )
    mock_sessionmaker.assert_called_once_with(
        autocommit=False, autoflush=False, bind=mock_engine
    )
    mock_scoped_session.assert_called_once_with(mock_SessionLocal)
    mock_create_all.assert_called_once_with(bind=mock_engine)

    # Check if db_session is set globally
    from app.database import db_session

    assert db_session == mock_db_session


@patch("app.database.create_engine")
@patch("app.database.sessionmaker")
@patch("app.database.scoped_session")
@patch("app.database.Base.metadata.create_all")
def test_init_db_default_db_url(
    mock_create_all,
    mock_scoped_session,
    mock_sessionmaker,
    mock_create_engine,
    monkeypatch,
):
    # Remove DATABASE_URL to test default
    monkeypatch.delenv("DATABASE_URL", raising=False)

    # Mock the engine
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine

    # Mock the sessionmaker
    mock_SessionLocal = MagicMock()
    mock_sessionmaker.return_value = mock_SessionLocal

    # Mock the scoped_session
    mock_db_session = MagicMock()
    mock_scoped_session.return_value = mock_db_session

    # Call init_db
    init_db(app=None)

    # Assertions
    mock_create_engine.assert_called_once_with(
        "sqlite:///./test.db", pool_pre_ping=True
    )
    mock_sessionmaker.assert_called_once_with(
        autocommit=False, autoflush=False, bind=mock_engine
    )
    mock_scoped_session.assert_called_once_with(mock_SessionLocal)
    mock_create_all.assert_called_once_with(bind=mock_engine)

    # Check if db_session is set globally
    from app.database import db_session

    assert db_session == mock_db_session


# -------------------- get_db Tests -------------------- #


@patch("app.database.db_session")
def test_get_db_success(mock_db_session):
    mock_db = MagicMock()
    mock_db_session.return_value = mock_db

    # Use the context manager
    with get_db() as db:
        assert db == mock_db
        mock_db_session.assert_called_once()

    # Ensure db.close() was called
    mock_db.close.assert_called_once()


@patch("app.database.db_session")
def test_get_db_sqlalchemy_error(mock_db_session):
    mock_db = MagicMock()
    mock_db_session.return_value = mock_db

    # Use the context manager and raise an exception inside the block
    with pytest.raises(SQLAlchemyError):
        with get_db() as db:
            raise SQLAlchemyError("Session error")

    # Ensure rollback and close were called
    mock_db.rollback.assert_called_once()
    mock_db.close.assert_called_once()


@patch("app.database.db_session")
def test_get_db_unexpected_error(mock_db_session):
    mock_db = MagicMock()
    mock_db_session.return_value = mock_db

    # Use the context manager and raise an unexpected exception inside the block
    with pytest.raises(Exception):
        with get_db() as db:
            raise SQLAlchemyError("Unexpected error")

    # Ensure rollback and close were called
    mock_db.rollback.assert_called_once()
    mock_db.close.assert_called_once()


# -------------------- Exception Handling in init_db -------------------- #


@patch(
    "app.database.create_engine", side_effect=SQLAlchemyError("Engine creation failed")
)
@patch("app.database.sessionmaker")
@patch("app.database.scoped_session")
@patch("app.database.Base.metadata.create_all")
def test_init_db_engine_creation_failure(
    mock_create_all, mock_scoped_session, mock_sessionmaker, mock_create_engine
):
    """
    Test that init_db raises SQLAlchemyError when engine creation fails.
    """
    with pytest.raises(SQLAlchemyError, match="Engine creation failed"):
        init_db(app=None)

    # Assertions
    mock_create_engine.assert_called_once()
    mock_sessionmaker.assert_not_called()
    mock_scoped_session.assert_not_called()
    mock_create_all.assert_not_called()


@patch("app.database.create_engine")
@patch(
    "app.database.sessionmaker",
    side_effect=SQLAlchemyError("Sessionmaker configuration failed"),
)
@patch("app.database.scoped_session")
@patch("app.database.Base.metadata.create_all")
def test_init_db_sessionmaker_failure(
    mock_create_all, mock_scoped_session, mock_sessionmaker, mock_create_engine
):
    """
    Test that init_db raises SQLAlchemyError when sessionmaker configuration fails.
    """
    # Arrange
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine

    with pytest.raises(SQLAlchemyError, match="Sessionmaker configuration failed"):
        init_db(app=None)

    # Assertions
    mock_create_engine.assert_called_once()
    mock_sessionmaker.assert_called_once()
    mock_scoped_session.assert_not_called()
    mock_create_all.assert_not_called()


@patch("app.database.create_engine")
@patch("app.database.sessionmaker")
@patch("app.database.scoped_session")
@patch("app.database.Base.metadata.create_all")
def test_init_db_scoped_session_failure(
    mock_create_all, mock_scoped_session, mock_sessionmaker, mock_create_engine
):
    """
    Test that init_db raises SQLAlchemyError when scoped_session creation fails.
    """
    # Arrange
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine

    mock_SessionLocal = MagicMock()
    mock_sessionmaker.return_value = mock_SessionLocal

    mock_scoped_session.side_effect = SQLAlchemyError("Scoped session creation failed")

    with pytest.raises(SQLAlchemyError, match="Scoped session creation failed"):
        init_db(app=None)

    # Assertions
    mock_create_engine.assert_called_once()
    mock_sessionmaker.assert_called_once()
    mock_scoped_session.assert_called_once()
    mock_create_all.assert_not_called()


@patch("app.database.create_engine")
@patch("app.database.sessionmaker")
@patch("app.database.scoped_session")
@patch(
    "app.database.Base.metadata.create_all",
    side_effect=SQLAlchemyError("create_all failed"),
)
def test_init_db_create_all_failure(
    mock_create_all, mock_scoped_session, mock_sessionmaker, mock_create_engine
):
    """
    Test that init_db raises SQLAlchemyError when Base.metadata.create_all fails.
    """
    # Arrange
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine

    mock_SessionLocal = MagicMock()
    mock_sessionmaker.return_value = mock_SessionLocal

    mock_db_session = MagicMock()
    mock_scoped_session.return_value = mock_db_session

    with pytest.raises(SQLAlchemyError, match="create_all failed"):
        init_db(app=None)

    # Assertions
    mock_create_engine.assert_called_once()
    mock_sessionmaker.assert_called_once()
    mock_scoped_session.assert_called_once()
    mock_create_all.assert_called_once_with(bind=mock_engine)
