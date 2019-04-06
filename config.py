"""Configuration module for the mealpoll app."""

import os

class Config():
    """Configuration class for the mealpoll app.

    Pulls configuration from environment variables.
    """

    # Root app directory (contains this file)
    APP_ROOT = os.path.abspath(os.path.dirname(__name__))

    # Secret key
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
        'change-this-insecure-key'

    # Database setup
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"sqlite:///{os.path.join(APP_ROOT, 'app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    if os.environ.get('FLASK_ENV') == 'development':
        SEND_FILE_MAX_AGE_DEFAULT = 0
