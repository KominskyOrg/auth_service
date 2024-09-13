import os
import logging
import bcrypt


def verify_password(stored_hashed_password, user_provided_password):
    """
    Verify if the provided password matches the stored hashed password.

    :param stored_hashed_password: The hashed password stored in the database.
    :param user_provided_password: The plain text password provided by the user.
    :return: True if the password matches, False otherwise.
    """
    try:
        return bcrypt.checkpw(
            user_provided_password.encode("utf-8"),
            stored_hashed_password.encode("utf-8"),
        )
    except Exception as e:
        logging.error(f"Error verifying password: {e}")
        return False


def get_stored_hashed_password(email):
    """
    Retrieve the stored hashed password for a given email.

    This is a mock function to simulate retrieving the hashed password from the database.

    :param email: The email address of the user.
    :return: The hashed password if the email matches the mock email, None otherwise.

    TODO: Add functionality to retrieve the salt from the database using the provided email.
    """
    mock_email = "test@example.com"
    # This should be the hashed password stored in your database
    mock_hashed_password = (
        "$2b$12$KIXQ4J1E1G1E1G1E1G1E1u1E1G1E1G1E1G1E1G1E1G1E1G1E1G1E"
    )
    if email == mock_email:
        return mock_hashed_password
    return None
