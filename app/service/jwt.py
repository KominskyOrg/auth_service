import jwt
import datetime
import os

SECRET_KEY = os.getenv("SECRET_KEY")


def generate_jwt(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.now(datetime.UTC) + datetime.timedelta(hours=1),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token
