"""Utilities for unit testing."""

from config import Config
from app import create_app
from app import db

class ModelTestConfig(Config):
    """App config for testing."""

    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class ModelTestMixin():
    """A mixin for model tests.

    Creates app object and in-memory database instance.
    """

    def setUp(self): #pylint: disable=invalid-name
        """Create an instance of the app with an in-memory database."""

        self.app = create_app(ModelTestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self): #pylint: disable=invalid-name
        """Remove our instance of the app and the associated in-memory database."""

        db.session.remove()
        db.drop_all()
        self.app_context.pop()