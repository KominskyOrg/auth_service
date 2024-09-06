# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from app.config import get_config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder='../html')
    
    # Load configuration
    config = get_config()
    app.config.from_object(config)

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)

    # Import and register blueprints
    from app.routes import auth_bp, main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app
