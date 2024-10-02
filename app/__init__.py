# app/__init__.py

import logging
from flask import Flask
from flask_cors import CORS
from app.routes import auth_service_bp
from app.config import get_config
from app.database import init_db
import os

def create_app():
    app = Flask(__name__)

    # Enable CORS
    CORS(app)

    # Set up detailed logging
    setup_logging(app)

    logger = app.logger
    logger.info("Creating the Flask application.")

    # Load configuration
    config = get_config()
    app.config.from_object(config)
    logger.info("Configuration loaded.")

    # Initialize the database
    init_db(app)
    logger.info("Database has been initialized.")

    # Register blueprints
    app.register_blueprint(auth_service_bp)
    logger.info("Auth service blueprint registered.")

    # Conditionally register Swagger UI in development environment
    if app.config.get("ENV") == "development":
        register_swagger_ui(app, logger)

    logger.info("Flask application creation complete.")
    return app


def setup_logging(app):
    """
    Configures logging for the Flask application.
    """
    # Remove default handlers to prevent duplicate logs
    for handler in app.logger.handlers[:]:
        app.logger.removeHandler(handler)

    # Create a stream handler for console output
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    # Define a detailed log format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    stream_handler.setFormatter(formatter)

    # Add the handler to the app's logger
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)

    # Optionally, add file logging for production
    if app.config.get("ENV") == "production":
        file_handler = logging.FileHandler('app.log')
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)


def register_swagger_ui(app, logger):
    """
    Registers Swagger UI for API documentation in development environment.
    """
    try:
        from flask_swagger_ui import get_swaggerui_blueprint

        SWAGGER_URL = "/api/docs"
        API_URL = "/static/swagger.yaml"

        swaggerui_blueprint = get_swaggerui_blueprint(
            SWAGGER_URL,
            API_URL,
            config={"app_name": "Auth Service"}
        )
        app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
        logger.info("Swagger UI has been registered at %s.", SWAGGER_URL)
    except ImportError:
        logger.error("Flask-Swagger-UI is not installed. Swagger UI not available.")
    except Exception as e:
        logger.error("Failed to register Swagger UI: %s", e)


app = create_app()
