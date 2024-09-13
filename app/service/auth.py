import logging


def login(email, password):
    # Simple mock login function for basic usage
    mock_email = "test@example.com"
    mock_password = "password123"  # This should be the decrypted password

    if email == mock_email and password == mock_password:
        return {"message": "Login successful", "token": "mock_jwt_token"}, 200
    else:
        return {"message": "Invalid email or password"}, 401


def register(email, password, salt):
    # existing_user = get_user_by_email(email)
    # if existing_user:
    #     return {"message": "Email/Username is already taken"}, 400

    try:
        # add_user(email, password, salt)
        return {"message": "Registration successful"}, 201
    except Exception as e:
        logging.error(f"Error registering user: {e}")
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
