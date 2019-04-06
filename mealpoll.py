"""Mealpoll App Entry Point"""
from app import create_app
from app import db
from app.auth.models import Admin

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'Admin':Admin}