from __future__ import annotations

import os

from dotenv import load_dotenv

from clovars import ROOT_PATH

load_dotenv(ROOT_PATH / '.env')
APP_PATH = ROOT_PATH / 'clovars' / 'app'


class Config:
    """Base class for setting Flask configuration."""
    FLASK_APP = os.environ.get('FLASK_APP')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SESSION_COOKIE_NAME = os.environ.get('SESSION_COOKIE_NAME')
    STATIC_FOLDER = APP_PATH / 'static'
    TEMPLATES_FOLDER = APP_PATH / 'templates'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(Config):
    """Class for setting Flask development configuration."""
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{APP_PATH / "test.db"}'
    SQLALCHEMY_ECHO = True


class ProdConfig(Config):
    """Class for setting Flask production configuration."""
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{APP_PATH / "app.db"}'
    SQLALCHEMY_ECHO = False
