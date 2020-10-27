from flask import Flask, render_template, request, flash, jsonify, redirect, session, g, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import requests

from models import db, connect_db, User, Fish, Caught, Uncaught
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
########## Load Fish Database ##########
def load_database():
    all_fish = get_all_fish()
    for fish in all_fish:
        name = fish['name']
        icon = fish['icon_url']
        new_fish = Fish(name=name, icon_url=icon)
        db.session.add(new_fish)
        db.session.commit()

########## API Calls ##########
def get_all_fish():
    """Make API call to load all fish to database.
    Return JSON {}"""
    response = requests.get(f'{API_BASE_URL}/fish')
    data = response.json()
    all_fish = []
    for d in data:
        name = d['name']['name-USen']
        icon = d['icon_uri']
        fish = {'name': name, 'icon_url': icon}
        all_fish.append(fish)
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

    If the there already is a user with that username: flash message
    and re-present form.
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
        return render_template('home.html')

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
# Track Creatures and Save routes:

@app.route('/track')
def show_index():
    """Show tracking page."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    #check if global user has previously saved caught/uncaught fish
    saved_uncaught_fish = Uncaught.query.filter_by(user_id=g.user.id).all()
    saved_caught_fish = Caught.query.filter_by(user_id=g.user.id).all()

    #if user already has saved fish, show last saved uncaught/caught sections
    if len(saved_caught_fish) != 0:
        return render_template('users/index-2.html', uncaught_fish=saved_uncaught_fish, caught_fish=saved_caught_fish)

    #if user's first time logging in or have no saved caught fish, then show all fish and save all uncaught fish to user's id in Uncaught table
    else:
        all_fish = Fish.query.all()
        for f in all_fish:
            uncaught_fish = Uncaught(user_id=g.user.id, fish_id=f.id)
            db.session.add(uncaught_fish)
            db.session.commit()
        return render_template('users/index-2.html', all_fish=all_fish)

@app.route('/save', methods=["POST"])
def save_fish():
    """Save uncaught/caught sections."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    #if fish are checked in the uncaught section, these are considered "caught"
    caught_fish = request.form.getlist('uncaughtfishcheckbox')

    #for each caught fish, save to Caught table with user's id, and delete fish from Uncaught table
    for f in caught_fish:
        caught_fish = Caught(user_id=g.user.id, fish_id=f)
        db.session.add(caught_fish)
        db.session.commit()
        update_uncaught = Uncaught.query.filter(Uncaught.user_id==g.user.id, Uncaught.fish_id==f).delete()
        db.session.commit()
    
    #if fish are checked in the caught section, these are considered "uncaught"
    uncaught_fish = request.form.getlist('caughtfishcheckbox')

    #for each uncaught fish, save to Uncaught table with user's id, and delete fish from Caught table
    for f in uncaught_fish:
        uncaught_fish = Uncaught(user_id=g.user.id, fish_id=f)
        db.session.add(uncaught_fish)
        db.session.commit()
        update_caught = Caught.query.filter(Caught.user_id==g.user.id, Caught.fish_id==f).delete()
        db.session.commit()

    return redirect('/track')