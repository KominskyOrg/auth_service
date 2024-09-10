# app/__init__.py

from flask import Flask
from app.routes import auth_service_bp
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # Register blueprints
    app.register_blueprint(auth_service_bp)

    # Conditionally register Swagger UI in development environment
    if app.config['ENV'] == 'development':
        from flask_swagger_ui import get_swaggerui_blueprint
        SWAGGER_URL = '/api/docs'
        API_URL = '/static/swagger.yaml'
        swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Auth Service"})
        app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app
