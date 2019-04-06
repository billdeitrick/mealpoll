"""Models for authentication."""

from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Admin(UserMixin, db.Model):
    """Application administrators."""

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(64), nullable=False)

    def set_password(self, password):
        """Set the user's password."""

        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check the user's password."""

        return check_password_hash(self.password_hash, password)
