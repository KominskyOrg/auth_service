# app/models.py

from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base
import logging

# Initialize the logger
logger = logging.getLogger(__name__)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True, nullable=False)

    def __init__(self, email, username, hashed_password, salt, first_name, last_name):
        logger.debug(f"Initializing User with username: {username}")
        self.email = email
        self.username = username
        self.password = hashed_password
        self.salt = salt
        self.first_name = first_name
        self.last_name = last_name
        self.is_active = True
        logger.info(f"User object created with username: {username}")

    def set_password(self, new_password):
        logger.debug(f"Setting new password for user: {self.username}")
        self.password = new_password
        logger.info(f"Password updated for user: {self.username}")

    def to_dict(self):
        logger.debug(f"Converting User object to dictionary: {self.username}")
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
