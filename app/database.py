# app/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from sqlalchemy.exc import SQLAlchemyError
import logging
from contextlib import contextmanager
import os

# Get the logger
logger = logging.getLogger(__name__)

# Base class for our class definitions
Base = declarative_base()


def init_db(app) -> None:
    database_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    logger.info("Initializing database")
    logger.debug(f"Database URL: {database_url}")

    # Create the SQLAlchemy engine
    engine = create_engine(database_url, pool_pre_ping=True)
    logger.info("SQLAlchemy engine created")

    # Create a configured "Session" class
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("SessionLocal configured")

    # Create a scoped session
    global db_session
    db_session = scoped_session(SessionLocal)
    logger.info("Scoped session created")


    logger.info("Models imported")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")


@contextmanager
def get_db():
    """Provides a database session for a request.
    Closes the session when done.
    """
    logger.debug("Getting database session")
    db = db_session()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database session rollback due to error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("Database session closed")
