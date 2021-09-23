# services/users/project/config.py


import os  # new


class BaseConfig:
    """Configuracion Base"""

    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "my_key"  # nuevo
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class DevelopmentConfig(BaseConfig):
    """Development configuration"""

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")  # new
    DEBUG_TB_ENABLED = True


class TestingConfig(BaseConfig):
    """Configuracion de Testing"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_TEST_URL")  # nuevo


class ProductionConfig(BaseConfig):
    """Configuracion de Production"""

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")  # nuevo
