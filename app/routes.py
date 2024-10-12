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
from app.database import get_db
import logging
from sqlalchemy.exc import SQLAlchemyError

# Get the logger
logger = logging.getLogger(__name__)

auth_service_bp = Blueprint("auth", __name__, url_prefix="/service/auth")


@auth_service_bp.route("/login", methods=["POST"])
def login_route():
    data = request.json
    logger.info("Login request received")
    logger.debug(f"Request data: {data}")

    try:
        with get_db() as db:
            response = handle_request(
                login, data.get("username"), data.get("password"), db=db
            )
            logger.debug(f"Response: {response}")
            return response
    except SQLAlchemyError as db_err:
        logger.error(f"Database error during login: {db_err}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@auth_service_bp.route("/register", methods=["POST"])
def register_route():
    data = request.json
    logger.info("Register request received")
    logger.debug(f"Request data: {data}")

    try:
        with get_db() as db:
            response = handle_request(
                register,
                data.get("email"),
                data.get("password"),
                data.get("first_name"),
                data.get("last_name"),
                data.get("username"),
                db=db,
            )
            logger.debug(f"Response: {response}")
            return response
    except SQLAlchemyError as db_err:
        logger.error(f"Database error during registration: {db_err}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@auth_service_bp.route("/logout", methods=["POST"])
def logout_route():
    logger.info("Logout request received")

    try:
        with get_db() as db:
            response = handle_request(logout, db=db)
            logger.debug(f"Response: {response}")
            return response
    except SQLAlchemyError as db_err:
        logger.error(f"Database error during logout: {db_err}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f"Unexpected error during logout: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@auth_service_bp.route("/reset-password", methods=["POST"])
def reset_password_route():
    data = request.json
    logger.info("Reset password request received")
    logger.debug(f"Request data: {data}")

    try:
        with get_db() as db:
            response = handle_request(reset_password, data.get("email"), db=db)
            logger.debug(f"Response: {response}")
            return response
    except SQLAlchemyError as db_err:
        logger.error(f"Database error during password reset: {db_err}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f"Unexpected error during password reset: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@auth_service_bp.route("/change-password", methods=["POST"])
def change_password_route():
    data = request.json
    logger.info("Change password request received")
    logger.debug(f"Request data: {data}")

    try:
        with get_db() as db:
            response = handle_request(
                change_password,
                data.get("old_password"),
                data.get("new_password"),
                db=db,
            )
            logger.debug(f"Response: {response}")
            return response
    except SQLAlchemyError as db_err:
        logger.error(f"Database error during password change: {db_err}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f"Unexpected error during password change: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@auth_service_bp.route("/deactivate-account", methods=["POST"])
def deactivate_account_route():
    data = request.json
    logger.info("Deactivate account request received")
    logger.debug(f"Request data: {data}")

    try:
        with get_db() as db:
            response = handle_request(
                deactivate_account, data.get("username"), data.get("password"), db=db
            )
            logger.debug(f"Response: {response}")
            return response
    except SQLAlchemyError as db_err:
        logger.error(f"Database error during account deactivation: {db_err}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f"Unexpected error during account deactivation: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@auth_service_bp.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint to verify that the auth_service is running.
    """
    return jsonify({"status": "OK"}), 200
