import jwt
import datetime
import os
import logging

# Get the logger
logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "smile-secret-key")

def generate_jwt(user_id):
    logger.info("Generating JWT")
    logger.debug(f"User ID: {user_id}")
    try:
        payload = {
            "user_id": user_id,
            "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1),
            "iat": datetime.datetime.now(datetime.UTC)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        logger.debug(f"Generated JWT: {token}")
        return token
    except Exception as e:
        logger.error(f"Error generating JWT: {e}", exc_info=True)
        return None
