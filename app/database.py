from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import logging

# Get the logger
logger = logging.getLogger(__name__)

# Base class for our classes definitions
Base = declarative_base()


def init_db(app):
    database_url = app.config["SQLALCHEMY_DATABASE_URI"]
    logger.info("Initializing database")
    logger.debug(f"Database URL: {database_url}")

    # Create the SQLAlchemy engine
    engine = create_engine(database_url)
    logger.info("SQLAlchemy engine created")

    # Create a configured "Session" class
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("SessionLocal configured")

    # Create a scoped session
    global db_session
    db_session = scoped_session(SessionLocal)
    logger.info("Scoped session created")

    import app.models

    logger.info("Models imported")

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")


# Dependency to get the database session
def get_db():
    logger.debug("Getting database session")
    db = db_session()
    try:
        yield db
    finally:
        db.close()
        logger.debug("Database session closed")
