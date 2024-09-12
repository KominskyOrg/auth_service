from flask import Blueprint, request
from app.service.utils.crypto import verify_password
from app.service.auth import login, register, logout, reset_password, change_password
from app.service.utils.request_handler import handle_request

auth_service_bp = Blueprint('auth', __name__, url_prefix='/service/auth')

@auth_service_bp.route('/login', methods=['POST'])
def login_route():
    data = request.json
    encrypted_password = data.get('password')
    if encrypted_password:
        data['password'] = verify_password(encrypted_password)
    return handle_request(login, data.get('email'), data.get('password'))

@auth_service_bp.route('/register', methods=['POST'])
def register_route():
    data = request.json
    return handle_request(register, data.get('email'), data.get('password'))

@auth_service_bp.route('/logout', methods=['POST'])
def logout_route():
    return handle_request(logout)

@auth_service_bp.route('/reset-password', methods=['POST'])
def reset_password_route():
    data = request.json
    return handle_request(reset_password, data.get('email'))

@auth_service_bp.route('/change-password', methods=['POST'])
def change_password_route():
    data = request.json
    return handle_request(change_password, data.get('old_password'), data.get('new_password'))
