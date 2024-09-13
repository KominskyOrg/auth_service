from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Base class for our classes definitions
Base = declarative_base()

def init_db(app):
    # Read the DATABASE_URL from the app configuration
    database_url = app.config['SQLALCHEMY_DATABASE_URI']
    
    # Create the SQLAlchemy engine
    engine = create_engine(database_url)
    
    # Create a configured "Session" class
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create a scoped session
    global db_session
    db_session = scoped_session(SessionLocal)
    
    # Import all modules here that might define models so that
    # they will be registered properly on the metadata. Otherwise,
    # you will have to import them first before calling init_db()
    import app.models
    Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()
