"""Models for ACNH Creature Tracker app."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """User."""

    __tablename__ = "users"

    id = db.Column(db.Integer,
                primary_key=True,
                autoincrement=True)
    username = db.Column(db.Text,
                nullable=False,
                unique=True)
    email = db.Column(db.Text,
                nullable=False,
                unique=True)
    password = db.Column(db.Text,
                nullable=False)
    profile_img = db.Column(db.Text,
                default="/static/images/default-pic.png")

class Fish(db.Model):
    """Fish."""

    __tablename__ = "fish"

    id = db.Column(db.Integer,
                primary_key=True,
                autoincrement=True)
    name = db.Column(db.Text,
                nullable=False,
                unique=True)

class Uncaught(db.Model):
    """Uncaught Fish."""

    __tablename__ = "uncaught_fish"

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )
    fish_id = db.Column(
        db.Integer,
        db.ForeignKey('fish.id', ondelete="cascade"),
        primary_key=True,
    )

class Caught(db.Model):
    """Caught Fish."""

    __tablename__ = "caught_fish"

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )
    fish_id = db.Column(
        db.Integer,
        db.ForeignKey('fish.id', ondelete="cascade"),
        primary_key=True,
    )