import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "app", "database", "app.db")

class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'key001'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
class DevelopmentConfig(Config):
    """Configuration pour l'environnement de développement."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.abspath(DB_PATH)}'
    ENV = 'development'

class TestingConfig(Config):
    """Configuration pour les tests."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.abspath(DB_PATH)}'
    ENV = 'testing'

class ProductionConfig(Config):
    """Configuration pour l'environnement de production."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.abspath(DB_PATH)}'
    ENV = 'production'

# Dictionnaire pour faciliter l'accès aux configurations par environnement
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

# Accès à la configuration par défaut
default_config = DevelopmentConfig