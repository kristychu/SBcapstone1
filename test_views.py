"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_views.py

from unittest import TestCase

from app import app, CURR_USER_KEY
from models import db, connect_db, User, Fish, User_Fish

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

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def load_fish(self):
        f1 = Fish(name="fish778", icon_url="fish778iconurl.jpg", catchphrase="fish778catchphrase")
        f1_id = 778
        f1.id = f1_id
        f2 = Fish(name="fish884", icon_url="fish884iconurl.jpg", catchphrase="fish884catchphrase")
        f2_id = 884
        f2.id = f2_id
        f3 = Fish(name="fish1", icon_url="fish1iconurl.jpg", catchphrase="fish1catchphrase")
        f4 = Fish(name="fish2", icon_url="fish2iconurl.jpg", catchphrase="fish2catchphrase")
        db.session.add_all([f1, f2, f3, f4])
        db.session.commit()
    
        uf778 = User_Fish(user_id=self.testuser_id, fish_id=f1.id, is_caught=False)
        uf884 = User_Fish(user_id=self.testuser_id, fish_id=f2.id, is_caught=False)
        uf1 = User_Fish(user_id=self.testuser_id, fish_id=f3.id, is_caught=False)
        uf2 = User_Fish(user_id=self.testuser_id, fish_id=f4.id, is_caught=False)
        db.session.add_all([uf778, uf884, uf1, uf2])
        db.session.commit()

        self.f1 = f1
        self.f2 = f2
        self.f3 = f3
        self.f4 = f4
    
    def test_show_home(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            resp = c.get("/")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("We currently only allow users to track fish.", str(resp.data))
    
    def test_show_all_fish(self):
        self.load_fish()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            resp = c.get('/fish')
            self.assertEqual(resp.status_code, 200)

            self.assertIn("fish1", str(resp.data))
            self.assertIn("fish2", str(resp.data))
            self.assertIn("fish778", str(resp.data))
            self.assertIn("fish884", str(resp.data))
            self.assertIn("fish1iconurl.jpg", str(resp.data))
            self.assertIn("fish2iconurl.jpg", str(resp.data))
            self.assertIn("fish778iconurl.jpg", str(resp.data))
            self.assertIn("fish884iconurl.jpg", str(resp.data))
    
    def test_show_one_fish(self):
        self.load_fish()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
        
        resp = c.get('/fish/1')

        self.assertEqual(resp.status_code, 200)
        self.assertIn("fish1", str(resp.data))
        self.assertNotIn("fish2", str(resp.data))
        self.assertIn("fish1iconurl.jpg", str(resp.data))
        self.assertNotIn("fish2iconurl.jpg", str(resp.data))

    def test_show_one_fish_json(self):
        self.load_fish()

        with self.client as c:
            url = f"/api/fish/{self.f1.id}"
            resp = c.get(url)

            self.assertEqual(resp.status_code, 200)
            data = resp.json
            self.assertEqual(data, {
                "fish": {
                    "id": self.f1.id,
                    "name": "fish778",
                    "icon_url": "fish778iconurl.jpg",
                    "catchphrase": "fish778catchphrase"
                }
            })
    
    def test_edit_fish_json(self):
        self.load_fish()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id  

        url = f"/api/users/{self.testuser_id}/fish/778"
        resp = c.patch(url)

        self.assertEqual(resp.status_code, 200)
        data = resp.json
        self.assertEqual(data, {
            "fish": {
                "user_id": self.testuser_id,
                "fish_id": 778,
                "is_caught": True
            }
        })