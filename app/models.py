# app/models.py

import logging
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

logger = logging.getLogger(__name__)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, email, username, hashed_password, salt, first_name, last_name):
        self.email = email
        self.username = username
        self.password = hashed_password
        self.salt = salt
        self.first_name = first_name
        self.last_name = last_name
        self.is_active = True
        self.created_at = None

        logger.debug(f"Initializing User with username: {username}")
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
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
