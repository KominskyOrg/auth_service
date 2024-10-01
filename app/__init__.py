# app/__init__.py

import logging
from flask import Flask
from app.routes import auth_service_bp
from app.config import get_config
from flask_cors import CORS
from app.database import init_db


def create_app():
    app = Flask(__name__)
    CORS(app)

    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = app.logger
    logger.info("Creating the Flask application.")

    # Load configuration
    app.config.from_object(get_config())
    logger.info("Configuration loaded.")

    # Initialize the database
    init_db(app)
    logger.info("Database has been initialized.")

    # Register blueprints
    app.register_blueprint(auth_service_bp)
    logger.info("Auth service blueprint registered.")

    # Conditionally register Swagger UI in development environment
    if app.config["ENV"] == "development":
        try:
            from flask_swagger_ui import get_swaggerui_blueprint

            SWAGGER_URL = "/api/docs"
            API_URL = "/static/swagger.yaml"
            swaggerui_blueprint = get_swaggerui_blueprint(
                SWAGGER_URL, API_URL, config={"app_name": "Auth Service"}
            )
            app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
            logger.info("Swagger UI has been registered at %s.", SWAGGER_URL)
        except Exception as e:
            logger.error("Failed to register Swagger UI: %s", e)

    logger.info("Flask application creation complete.")
    return app


app = create_app()