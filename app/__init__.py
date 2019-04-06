#pylint: disable=invalid-name,wrong-import-position

"""Initialize the mealpoll application."""

from flask import Flask
from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import Config

# Instantiate extensions
# region
# Database
db = SQLAlchemy()
migrate = Migrate()

# Authentication
login = LoginManager()
login.login_view = 'auth.login'

# Bootstrap
bootstrap = Bootstrap()
# endregion

def create_app(config=Config):
    """Create an instance of the application using the supplied config object."""

    app = Flask(__name__)
    app.config.from_object(config)

    # Init db extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Init login extension
    login.init_app(app)

    # Init Bootstrap extension
    bootstrap.init_app(app)

    # Register primary application blueprint
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # Register the authentication blueprint
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app

# Avoiding circular import
from app.auth.models import Admin

@login.user_loader
def user_loader(admin_id):
    """User loader function for Flask-Login."""

    return Admin.query.get(admin_id)
