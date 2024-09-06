from flask import Blueprint, request, jsonify
from app.auth_service import login, register, logout, reset_password, change_password

auth_bp = Blueprint('auth', __name__, url_prefix='/service/auth')

@auth_bp.route('/login', methods=['POST'])
def login_route():
    data = request.json
    response, status_code = login(data.get('email'), data.get('password'))
    return jsonify(response), status_code

@auth_bp.route('/register', methods=['POST'])
def register_route():
    data = request.json
    response, status_code = register(data.get('email'), data.get('password'))
    return jsonify(response), status_code

@auth_bp.route('/logout', methods=['POST'])
def logout_route():
    response, status_code = logout()
    return jsonify(response), status_code

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password_route():
    data = request.json
    response, status_code = reset_password(data.get('email'))
    return jsonify(response), status_code

@auth_bp.route('/change-password', methods=['POST'])
def change_password_route():
    data = request.json
    response, status_code = change_password(data.get('old_password'), data.get('new_password'))
    return jsonify(response), status_code

# Remove the main_bp and index route as they're not auth-specific
