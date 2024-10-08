import logging
import bcrypt
from app.models import User
from app.database import get_db
from app.service.jwt import generate_jwt
from app.utils.exceptions import ValidationError, AuthenticationError, AuthorizationError, DatabaseError
from app.schemas.auth_schemas import RegisterSchema, LoginSchema, ResetPasswordSchema, ChangePasswordSchema, DeactivateAccountSchema
from sqlalchemy.exc import SQLAlchemyError

# Get the logger
logger = logging.getLogger(__name__)

def register(*args, db=None, **kwargs):
    schema = RegisterSchema()
    try:
        data = schema.load({
            "email": args[0],
            "password": args[1],
            "first_name": args[2],
            "last_name": args[3],
            "username": args[4],
        })
    except ValidationError as ve:
        raise ValidationError(ve.message)

    email = data['email']
    password = data['password']
    first_name = data['first_name']
    last_name = data['last_name']
    username = data['username']

    try:
        logger.info("Registering new user")
        logger.debug(f"User details: email={email}, username={username}")

        # Check if the email or username is already in use
        existing_user = (
            db.query(User)
            .filter((User.email == email) | (User.username == username))
            .first()
        )
        if existing_user:
            if existing_user.is_active:
                logger.warning("Email or username is already in use")
                raise ValidationError({"message": "Email or username is already in use"})
            else:
                # Reactivate the existing user
                logger.info("Reactivating existing user")
                existing_user.password = bcrypt.hashpw(
                    password.encode("utf-8"), bcrypt.gensalt()
                ).decode("utf-8")
                existing_user.first_name = first_name
                existing_user.last_name = last_name
                existing_user.username = username
                existing_user.is_active = True
                db.commit()
                logger.info("Account reactivated successfully")
                return {"message": "Account reactivated successfully"}, 200

        # Encrypt the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

        # Create a new user and add to the database
        new_user = User(
            email=email,
            username=username,
            hashed_password=hashed_password.decode("utf-8"),
            salt=salt.decode("utf-8"),
            first_name=first_name,
            last_name=last_name,
        )
        db.add(new_user)
        db.commit()
        logger.info("Registration successful")
        return {"message": "Registration successful"}, 201
    except SQLAlchemyError as db_err:
        logger.error(f"Database error during registration: {db_err}", exc_info=True)
        db.rollback()
        raise DatabaseError()
    except ValidationError as ve:
        raise ve
    except Exception as e:
        logger.exception(f"Error registering user: {e}")
        raise

def login(*args, db=None, **kwargs):
    schema = LoginSchema()
    try:
        data = schema.load({
            "username": args[0],
            "password": args[1],
        })
    except ValidationError as ve:
        raise ValidationError(ve.message)

    username = data['username']
    password = data['password']

    try:
        logger.info("Login attempt")
        logger.debug(f"Username: {username}")

        user = db.query(User).filter_by(username=username).first()
        if not user:
            logger.warning("Invalid username or password")
            raise AuthenticationError("Invalid username or password")

        if not user.is_active:
            logger.warning("User account is inactive")
            raise AuthorizationError("User account is inactive")

        # Retrieve the salt and encrypted password from the database
        salt = user.salt.encode("utf-8")
        encrypted_password = user.password.encode("utf-8")

        # Hash the provided password using the retrieved salt
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

        # Compare the hashed passwords
        if hashed_password != encrypted_password:
            logger.warning("Invalid username or password")
            raise AuthenticationError("Invalid username or password")

        token = generate_jwt(user.id)
        if not token:
            logger.error("Failed to generate JWT")
            raise Exception("JWT generation failed")

        logger.info("Login successful")
        return {"message": "Login successful", "token": token}, 200
    except (AuthenticationError, AuthorizationError) as ae:
        raise ae
    except SQLAlchemyError as db_err:
        logger.error(f"Database error during login: {db_err}", exc_info=True)
        raise DatabaseError()
    except Exception as e:
        logger.exception(f"Error logging in user: {e}")
        raise


def validate_email(email):
    email_regex = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    is_valid = re.match(email_regex, email) is not None
    logger.debug(f"Validating email: {email}, Valid: {is_valid}")
    return is_valid


def validate_name(name):
    name_regex = r"^[a-zA-Z]+$"
    is_valid = re.match(name_regex, name) is not None
    logger.debug(f"Validating name: {name}, Valid: {is_valid}")
    return is_valid


def logout():
    logger.info("Logout request received")
    # Simple mock logout function for basic usage
    return {"message": "Logout successful"}, 200


def reset_password(email):
    logger.info("Reset password request received")
    logger.debug(f"Email: {email}")
    # Simple mock reset password function for basic usage
    return {"message": "Password reset link sent to email"}, 200


def change_password(old_password, new_password):
    logger.info("Change password request received")
    logger.debug(f"Old password: {old_password}, New password: {new_password}")
    # Simple mock change password function for basic usage
    mock_old_password = "password123"  # This should be the decrypted old password

    if old_password == mock_old_password:
        logger.info("Password changed successfully")
        return {"message": "Password changed successfully"}, 200
    else:
        logger.warning("Invalid old password")
        return {"message": "Invalid old password"}, 401


def deactivate_account(username, password):
    try:
        db = next(get_db())
        logger.info("Deactivate account request received")
        logger.debug(f"Username: {username}")

        user = db.query(User).filter_by(username=username).first()

        if not user:
            logger.warning("Invalid username or password")
            return {"error": "Invalid username or password"}, 400

        # Retrieve the salt and encrypted password from the database
        salt = user.salt.encode("utf-8")
        encrypted_password = user.password.encode("utf-8")

        # Hash the provided password using the retrieved salt
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

        # Compare the hashed passwords
        if hashed_password != encrypted_password:
            logger.warning("Invalid username or password")
            return {"error": "Invalid username or password"}, 400

        # Deactivate the account
        user.is_active = False
        db.commit()
        logger.info("Account deactivated successfully")
        return {"message": "Account deactivated successfully"}, 200
    except Exception as e:
        logger.error(f"Error deactivating account: {e}", exc_info=True)
        return {"message": "Internal server error"}, 500
