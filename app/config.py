import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    True
    
class LocalConfig(Config):
    DEBUG = True
    ENV = 'development'

class DevConfig(Config):
    DEBUG = False
    ENV = 'development'

class ProdConfig(Config):
    DEBUG = False
    ENV = 'production'

def get_config():
    env = os.getenv('FLASK_ENV', 'local')
    if env == 'local':
        return LocalConfig
    elif env == 'development':
        return DevConfig
    elif env == 'production':
        return ProdConfig
    else:
        raise ValueError(f"Unknown environment: {env}")
    
