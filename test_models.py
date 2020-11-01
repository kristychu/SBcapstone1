"""User model tests."""

# run these tests like:
#
#    python -m unittest test_models.py

from unittest import TestCase
from sqlalchemy import exc

from app import app
from models import db, User, Fish, User_Fish

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///test-acnh"
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

class UserModelTestCase(TestCase):
    """Test views for user."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.register("test1", "email1@email.com", "password", None)
        uid1 = 1111
        u1.id = uid1

        u2 = User.register("test2", "email2@email.com", "password", None)
        uid2 = 2222
        u2.id = uid2

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            username="testuser",
            email="test@test.com",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have 1 fish registered
        self.assertEqual(len(u.fish), 0)
    
    ###### Signup Tests ######
    def test_valid_signup(self):
        u_test = User.register("testtesttest", "testtest@test.com", "password", None)
        uid = 99999
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "testtesttest")
        self.assertEqual(u_test.email, "testtest@test.com")
        self.assertNotEqual(u_test.password, "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        invalid = User.register(None, "test@test.com", "password", None)
        uid = 123456789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid = User.register("testtest", None, "password", None)
        uid = 123789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.register("testtest", "email@email.com", "", None)
        
        with self.assertRaises(ValueError) as context:
            User.register("testtest", "email@email.com", None, None)
    
    ###### Authentication Tests ######
    def test_valid_authentication(self):
        u = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid1)
    
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "badpassword"))

class FishModelTestCase(TestCase):
    """Test views for fish."""

    def setUp(self):
        """Make demo data."""

        Fish.query.delete()
        db.session.commit()

        fish = Fish(name='TestFish', icon_url="testiconurl.jpg")
        db.session.add(fish)
        db.session.commit()

        self.fish_id = fish.id

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()
    
    def test_fish_model(self):
        """Does basic model work?"""

        f = Fish(
            name='Fish1',
            icon_url="fish1iconurl.jpg"
        )

        db.session.add(f)
        db.session.commit()

        # Fish should have 0 user_fish relationship
        self.assertEqual(len(f.user_fish), 0)
    
    def test_duplicate_fish_iconurl(self):
        
        f1 = Fish(
            name='Fish1',
            icon_url="fish1iconurl.jpg"
        )

        f2 = Fish(
            name='Fish1',
            icon_url="fish1iconurl.jpg"
        )

        db.session.add_all([f1, f2])
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()