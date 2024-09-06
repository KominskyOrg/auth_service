import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret')

    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT', 3306)
    DB_NAME = os.getenv('DB_NAME')

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

class LocalConfig(Config):
    DEBUG = True
    BASE_URL = 'http://auth_service:5000'
    
class DevConfig(Config):
    DEBUG = False

class ProdConfig(Config):
    DEBUG = False

def get_config():
    env = os.getenv('FLASK_ENV', 'local')
    if env == 'local':
        return LocalConfig
    elif env == 'dev':
        return DevConfig
    elif env == 'prod':
        return ProdConfig
    else:
        raise ValueError(f"Unknown environment: {env}")
