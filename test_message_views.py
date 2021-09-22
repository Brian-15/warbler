"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
import pdb
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()
        
        msg = Message(
            text="TEXT",
            user_id=self.testuser.id
        )

        db.session.add(msg)
        db.session.commit()

        self.testmsg = Message.query.get(msg.id)

    def tearDown(self):
        """Clear tables"""

        User.query.delete()
        Message.query.delete()

    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                
            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            self.assertEqual(len(Message.query.all()), 2)

    def test_show_message(self):
        """Can show message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get(f"/messages/{self.testmsg.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.testmsg.text, html)
            self.assertIn("Delete", html)

    def test_delete_message(self):
        """Can delete message?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.post(f"/messages/{self.testmsg.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.testuser.username, html)
            self.assertFalse(Message.query.filter_by(user_id=self.testuser.id).first())
    
    def test_home_display(self):
        """Does the message properly show itself on home page"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.testmsg.text, html)
            