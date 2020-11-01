from flask import Flask, render_template, request, flash, jsonify, redirect, session, g, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import requests

from models import db, connect_db, User, Fish, User_Fish
from forms import UserAddForm, LoginForm

CURR_USER_KEY = "curr_user"
API_BASE_URL = "https://acnhapi.com/v1a"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///acnhcreatures'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = "SEEKRET!"

connect_db(app)
db.create_all()

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

##############################################################################
########## API Calls ##########
def get_all_fish():
    """Make API call for all fish."""
    response = requests.get(f'{API_BASE_URL}/fish')
    data = response.json()
    all_fish = []
    for d in data:
        name = d['name']['name-USen']
        icon = d['icon_uri']
        fish = {'name': name, 'icon_url': icon}
        all_fish.append(fish)
    return all_fish

########## Load Fish Database ##########
def load_database():
    """Load all fish from API to database."""
    all_fish = get_all_fish()
    for fish in all_fish:
        name = fish['name']
        icon = fish['icon_url']
        new_fish = Fish(name=name, icon_url=icon)
        db.session.add(new_fish)
        db.session.commit()

########## Return JSON ##########
def json_all_fish():
    """Make API call and 
    return JSON { 'id': id, 'name': name, 'icon_url': icon_url }"""
    all_fish = get_all_fish()
    response_json = jsonify(fish=all_fish)
    return (response_json, 201)

##############################################################################
# User register/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/register', methods=["GET", "POST"])
def signup():
    """Handle user registration.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If there already is a user with that username: flash message
    and re-present form.
    
    When user registers, save all fish to user's id in Users_Fish DB as uncaught.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.register(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                profile_img=form.profile_img.data or User.profile_img.default.arg,
            )
            db.session.commit()
        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/register.html', form=form)

        do_login(user)
        add_user_to_g()
        #when user registers, save all uncaught fish to user's id in Users_Fish table as uncaught
        create_user_uncaught_fish()
        return redirect("/")

    else:
        return render_template('users/register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash("You have successfully logged out!", "success")
    return redirect('/login')

##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage."""

    if g.user:
        return render_template('home.html', user=g.user)

    else:
        return render_template('home-anon.html')

#error handlers for 404 and 500 below copied 
# from Julian Nash's Youtube tutorial video: Flask error handling - Python on the web - Learning Flask Ep. 18
@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html')

@app.errorhandler(500)
def server_error(e):
    app.logger.error(f"Server error: {e}, route: {request.url}")
    return render_template('errors/500.html')

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html')

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('errors/405.html')

##############################################################################
# Helpers:

def create_user_uncaught_fish():
    all_fish = Fish.query.all()
    for f in all_fish:
        uncaught_fish = User_Fish(user_id=g.user.id, fish_id=f.id, is_caught=False)
        db.session.add(uncaught_fish)
        db.session.commit()

def toggle_is_caught(fish):
    if fish.is_caught == False:
        fish.is_caught = True
        db.session.commit()
        flash(f"Great job! You caught {fish.fish.name}! Keep it up!", "success")

    else:
        fish.is_caught = False
        db.session.commit()
        flash(f"Oops! You'll catch 'em next time!", "warning")
##############################################################################
# Fish routes:

@app.route('/fish')
def show_all_fish():
    """Show all user's fish."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(g.user.id)
    all_fish = User_Fish.query.filter(User_Fish.user_id==user.id).all()
    
    return render_template('users/index-2.html', all_fish=all_fish, user=user)

@app.route('/fish/<int:fish_id>')
def show_one_fish(fish_id):
    """Show details on one of user's fish."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    fish = Fish.query.get_or_404(fish_id)

    return render_template('users/fishdetail.html', fish=fish)

@app.route('/fish/<int:fish_id>/edit', methods=["GET", "PUT"])
def edit_fish(fish_id):
    """Update caught status of fish."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    fish = User_Fish.query.filter(User_Fish.user_id==g.user.id, User_Fish.fish_id==fish_id).first()
    toggle_is_caught(fish)

    return redirect('/fish')