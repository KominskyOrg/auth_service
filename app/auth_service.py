from app.models import User

def login(email, password):
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        # Generate and return token
        return {"message": "Logged in successfully"}, 200
    return {"error": "Invalid email or password"}, 401