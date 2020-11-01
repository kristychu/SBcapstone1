"""Models for ACNH Creature Tracker app."""
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
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

    fish = db.relationship('Fish', secondary='users_fish', backref='user')

    def __repr__(self):
        return f"<User {self.username} {self.email} >"

    @classmethod
    def register(cls, username, email, password, profile_img):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            profile_img=profile_img,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class Fish(db.Model):
    """Fish."""

    __tablename__ = "fish"

    id = db.Column(db.Integer,
                primary_key=True,
                autoincrement=True)
    name = db.Column(db.Text,
                nullable=False,
                unique=True)
    icon_url = db.Column(db.Text,
                nullable=False,
                unique=True)
    catchphrase = db.Column(db.Text,
                nullable=False)
    
    user_fish = db.relationship('User_Fish', backref='fish')

    def __repr__(self):
        return f"<Fish {self.name} {self.icon_url} >"

class User_Fish(db.Model):
    """User_Fish relationship."""

    __tablename__ = "users_fish"

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True)
    fish_id = db.Column(
        db.Integer,
        db.ForeignKey('fish.id', ondelete="cascade"),
        primary_key=True)
    is_caught = db.Column(db.Boolean,
            nullable=False)