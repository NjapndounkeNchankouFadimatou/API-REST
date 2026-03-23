"""
database.py – SQLAlchemy instance (single source of truth)
Import `db` everywhere; never create a second SQLAlchemy() instance.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Bind the SQLAlchemy instance to a Flask app and create all tables."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
