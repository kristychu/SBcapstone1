"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_views.py

from unittest import TestCase

from app import app, CURR_USER_KEY
from models import db, connect_db, User, Fish, Uncaught, Caught

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///test-acnh"
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.register(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    profile_img=None)
        self.testuser_id = 8989
        self.testuser.id = self.testuser_id

        db.session.commit()
    
    def load_fish(self):
        f1 = Fish(name="fish778", icon_url="fish778iconurl.jpg")
        f1_id = 778
        f1.id = f1_id
        f2 = Fish(name="fish884", icon_url="fish884iconurl.jpg")
        f2_id = 884
        f2.id = f2_id
        f3 = Fish(name="fish1", icon_url="fish1iconurl.jpg")
        f4 = Fish(name="fish2", icon_url="fish2iconurl.jpg")
        db.session.add_all([f1, f2, f3, f4])
        db.session.commit()
    
    def saved_user_fish(self):
        caught_fish = Caught(user_id=self.testuser_id, fish_id=f1_id)
        uncaught_fish = Uncaught(
            user_id=self.testuser_id, fish_id=f2_id,
            user_id=self.testuser_id, fish_id=f2_id,
            user_id=self.testuser_id, fish_id=f2_id
            )


    def test_show_home(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            resp = c.get("/")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("We currently only allow users to track fish.", str(resp.data))
    
    def test_show_index(self):
        self.load_fish()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            resp = c.get("/track")
            self.assertEqual(resp.status_code, 200)

            #Should show all fish names and fish icon urls under "Uncaught Fish" section
            #In order to know they are all in Uncaught section, the Caught section says "You haven't caught any yet!"
            self.assertIn("<h4>Uncaught Fish</h4>", str(resp.data))
            self.assertIn("<h4>Caught Fish</h4>", str(resp.data))
            self.assertIn("You haven\\\'t caught any yet!", str(resp.data))
            self.assertIn("fish1", str(resp.data))
            self.assertIn("fish2", str(resp.data))
            self.assertIn("fish778", str(resp.data))
            self.assertIn("fish884", str(resp.data))
            self.assertIn("fish1iconurl.jpg", str(resp.data))
            self.assertIn("fish2iconurl.jpg", str(resp.data))
            self.assertIn("fish778iconurl.jpg", str(resp.data))
            self.assertIn("fish884iconurl.jpg", str(resp.data))
    
    def test_save_caught_fish(self):
        self.load_fish()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
        
        caught_fish = ["1", "2"]
        resp = c.post("/save/caught", data={"uncaughtfishcheckbox": caught_fish}, follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("You haven\\\'t caught any yet!", str(resp.data))
        self.assertIn("fish1", str(resp.data))
        self.assertIn("fish2", str(resp.data))
        self.assertIn("Great job! Keep it up!", str(resp.data))

    def test_move_uncaught_fish(self):
        self.load_fish()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
        
        uncaught_fish = ["1"]
        resp = c.post("/save/uncaught", data={"caughtfishcheckbox": uncaught_fish}, follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Oops! You'll catch 'em next time!", str(resp.data))