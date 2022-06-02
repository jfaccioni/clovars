from __future__ import annotations

import os

from dotenv import load_dotenv

from clovars import ROOT_PATH

load_dotenv(ROOT_PATH / '.env')
APP_PATH = ROOT_PATH / 'clovars' / 'app'


class Config:
    """Base class for setting Flask configuration."""
    FLASK_APP = os.environ.get('FLASK_APP')
    FLASK_ENV = os.environ.get('FLASK_ENV')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SESSION_COOKIE_NAME = os.environ.get('SESSION_COOKIE_NAME')
    STATIC_FOLDER = APP_PATH / 'static'
    TEMPLATES_FOLDER = APP_PATH / 'templates'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(Config):
    """Class for setting Flask development configuration."""
    DEBUG = True
    TESTING = True
    TEMPLATES_AUTO_RELOAD = True
    ASSETS_DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{APP_PATH / "test.db"}'
    SQLALCHEMY_ECHO = False


class ProdConfig(Config):
    """Class for setting Flask production configuration."""
    DEBUG = False
    TESTING = False
    TEMPLATES_AUTO_RELOAD = False
    ASSETS_DEBUG = False
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{APP_PATH / "app.db"}'
    SQLALCHEMY_ECHO = False
