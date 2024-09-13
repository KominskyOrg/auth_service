import logging
import re
import bcrypt
from app.models import User
from app.database import get_db
from app.service.jwt import generate_jwt

def validate_email(email):
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(email_regex, email) is not None

def validate_name(name):
    name_regex = r'^[a-zA-Z]+$'
    return re.match(name_regex, name) is not None

def register(email, password, first_name, last_name, username):
    try:
        db = next(get_db())
        # Validate email and name formats
        if not validate_email(email):
            return {"message": "Invalid email format"}, 400
        if not validate_name(first_name) or not validate_name(last_name):
            return {"message": "Names can only contain letters"}, 400

        # Check if the email or username is already in use
        existing_user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        if existing_user:
            if existing_user.is_active:
                return {"message": "Email or username is already in use"}, 400
            else:
                # Reactivate the existing user
                existing_user.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                existing_user.first_name = first_name
                existing_user.last_name = last_name
                existing_user.username = username
                existing_user.is_active = True
                db.commit()
                return {"message": "Account reactivated successfully"}, 200

        # Encrypt the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        # Create a new user and add to the database
        new_user = User(
            email=email,
            password=hashed_password.decode('utf-8'),
            salt=salt.decode('utf-8'),
            first_name=first_name,
            last_name=last_name,
            username=username,
            is_active=True  # Set is_active to True by default
        )
        db.add(new_user)
        db.commit()

        return {"message": "Registration successful"}, 201
    except Exception as e:
        logging.error(f"Error registering user: {e}")
        return {"message": "Internal server error"}, 500

def login(username, password):
    try:
        db = next(get_db())
        user = db.query(User).filter_by(username=username).first()
        if not user:
            return {"message": "Invalid username or password"}, 401

        if not user.is_active:
            return {"message": "User account is inactive"}, 403

        # Retrieve the salt and encrypted password from the database
        salt = user.salt.encode('utf-8')
        encrypted_password = user.password.encode('utf-8')

        # Hash the provided password using the retrieved salt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        # Compare the hashed passwords
        if hashed_password == encrypted_password:
            token = generate_jwt(user.id)
            return {"message": "Login successful", "token": token}, 200
        else:
            return {"message": "Invalid username or password"}, 401
    except Exception as e:
        logging.error(f"Error logging in user: {e}")
        return {"message": "Internal server error"}, 500

def logout():
    # Simple mock logout function for basic usage
    return {"message": "Logout successful"}, 200

def reset_password(email):
    # Simple mock reset password function for basic usage
    return {"message": "Password reset link sent to email"}, 200

def change_password(old_password, new_password):
    # Simple mock change password function for basic usage
    mock_old_password = (
        "password123"  # This should be the decrypted old password
    )

    if old_password == mock_old_password:
        return {"message": "Password changed successfully"}, 200
    else:
        return {"message": "Invalid old password"}, 401
