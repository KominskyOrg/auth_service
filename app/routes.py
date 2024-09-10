from flask import Blueprint, request, jsonify, current_app
from service.utils.crypto import decrypt_password
from app.service.auth import login, register, logout, reset_password, change_password

auth_service_bp = Blueprint('auth', __name__, url_prefix='/service/auth')

SECRET_KEY = current_app.config['SECRET_KEY']


@auth_service_bp.route('/login', methods=['POST'])
def login_route():
    data = request.json
    encrypted_password = data.get('password')
    if encrypted_password:
        data['password'] = decrypt_password(encrypted_password, SECRET_KEY)
    response, status_code = login(data.get('email'), data.get('password'))
    return jsonify(response), status_code

@auth_service_bp.route('/register', methods=['POST'])
def register_route():
    data = request.json
    response, status_code = register(data.get('email'), data.get('password'))
    return jsonify(response), status_code

@auth_service_bp.route('/logout', methods=['POST'])
def logout_route():
    response, status_code = logout()
    return jsonify(response), status_code

@auth_service_bp.route('/reset-password', methods=['POST'])
def reset_password_route():
    data = request.json
    response, status_code = reset_password(data.get('email'))
    return jsonify(response), status_code

@auth_service_bp.route('/change-password', methods=['POST'])
def change_password_route():
    data = request.json
    response, status_code = change_password(data.get('old_password'), data.get('new_password'))
    return jsonify(response), status_code
