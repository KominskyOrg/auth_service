from flask import Blueprint, request, jsonify
from app.service.auth import (
    login,
    register,
    logout,
    reset_password,
    change_password,
    deactivate_account,
)
from app.utils.request_handler import handle_request
import logging

# Get the logger
logger = logging.getLogger(__name__)

auth_service_bp = Blueprint("auth", __name__, url_prefix="/service/auth")


@auth_service_bp.route("/login", methods=["POST"])
def login_route():
    data = request.json
    logger.info("Login request received")
    logger.debug(f"Request data: {data}")
    response = handle_request(login, data.get("username"), data.get("password"))
    logger.debug(f"Response: {response}")
    return response


@auth_service_bp.route("/register", methods=["POST"])
def register_route():
    data = request.json
    logger.info("Register request received")
    logger.debug(f"Request data: {data}")
    response = handle_request(
        register,
        data.get("email"),
        data.get("password"),
        data.get("first_name"),
        data.get("last_name"),
        data.get("username"),
    )
    logger.debug(f"Response: {response}")
    return response


@auth_service_bp.route("/logout", methods=["POST"])
def logout_route():
    logger.info("Logout request received")
    response = handle_request(logout)
    logger.debug(f"Response: {response}")
    return response


@auth_service_bp.route("/reset-password", methods=["POST"])
def reset_password_route():
    data = request.json
    logger.info("Reset password request received")
    logger.debug(f"Request data: {data}")
    response = handle_request(reset_password, data.get("email"))
    logger.debug(f"Response: {response}")
    return response


@auth_service_bp.route("/change-password", methods=["POST"])
def change_password_route():
    data = request.json
    logger.info("Change password request received")
    logger.debug(f"Request data: {data}")
    response = handle_request(
        change_password, data.get("old_password"), data.get("new_password")
    )
    logger.debug(f"Response: {response}")
    return response


@auth_service_bp.route("/deactivate-account", methods=["POST"])
def deactivate_account_route():
    data = request.json
    logger.info("Deactivate account request received")
    logger.debug(f"Request data: {data}")
    response = handle_request(
        deactivate_account, data.get("username"), data.get("password")
    )
    logger.debug(f"Response: {response}")
    return response


@auth_service_bp.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint to verify that the auth_service is running.
    """
    return jsonify({"status": "OK"}), 200