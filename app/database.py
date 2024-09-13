from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


def init_db(app):
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create the database tables
    Base.metadata.create_all(bind=engine)

    # Attach the session to the app
    app.session = SessionLocal


def get_db(app):
    db = app.session()
    try:
        yield db
    finally:
        db.close()
