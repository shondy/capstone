import os
#basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_sekret')
    # SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    uri = os.getenv("DATABASE_URL")
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = uri
    # rest of connection code using the connection string `uri`


class ProductionConfig(Config):
    DEBUG = False

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    uri = os.getenv("DATABASE_URL")
    SQLALCHEMY_DATABASE_URI = uri + '_test'