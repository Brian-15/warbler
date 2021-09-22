"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
import pdb
from unittest import TestCase

from models import Follows, db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY, users_followers

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UsereViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        u = User.signup(username="testuser",
                        email="test@test.com",
                        password="testuser",
                        image_url=None)
        db.session.add(u)
        db.session.commit()

        self.testuser = User.query.filter_by(username=u.username).one()

        msg = Message(
            text="text",
            user_id=self.testuser.id
        )

        db.session.add(msg)
        db.session.commit()

        self.testmessage = Message.query.get(msg.id)

    def tearDown(self):
        """Clear tables"""

        User.query.delete()
        Message.query.delete()

    def test_logout(self):
        """Can user properly log out?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get("/logout", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<h2 class=\"join-message\">Welcome back.</h2>", html)

    def test_home_logged_in(self):
        """Can user see the proper home page when logged in?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.testuser.username, html)

    def test_follow_views_logged_in(self):
        """Can user see followed / following views for any user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            User.signup("test", "test@test.net", "PASSWORD", "")
            u = User.query.filter_by(username="test").one()

            db.session.add(Follows(
                user_being_followed_id=u.id,
                user_following_id=self.testuser.id
            ))
            db.session.commit()

            resp = c.get(f"/users/{self.testuser.id}/following")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(u.username, html)

            resp = c.get(f"/users/{u.id}/followers")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.testuser.username, html)
    
    def test_follow_views_logged_out(self):
        """Can user see follower / following views for any user when logged out?"""

        with self.client as c:

            resp = c.get(f"/users/{self.testuser.id}/following")
            
            self.assertEqual(resp.status_code, 302)

            resp = c.get(f"/users/{self.testuser.id}/followers")

            self.assertEqual(resp.status_code, 302)

    def test_new_message_logged_in(self):
        """Can user create new message when logged in?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.post(f"/messages/new",
                          data={"text": "TEST_TEXT"},
                          follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn("TEST_TEXT", html)
    
    def test_new_message_logged_out(self):
        """Can user create new message when logged out?"""

        with self.client as c:

            resp = c.get(f"/messages/new", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertEqual(len(Message.query.all()), 1)

    def test_delete_message_logged_in(self):
        """Can a logged in user delete their own message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            msg = Message(text="TEST_TEXT", user_id=self.testuser.id)

            db.session.add(msg)
            db.session.commit()

            msg = Message.query.filter_by(text="TEST_TEXT").one()

            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn(msg.text, html)
            self.assertFalse(Message.query.filter_by(id=msg.id).one_or_none())
    
    def test_delete_another_users_message_logged_in(self):
        """Can a logged in user delete another user's message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            User.signup("foo", "foo@foo.foo", "foontastic", "")
            
            u = User.query.filter_by(username="foo").one()

            msg = Message(text="TEST_TEXT", user_id=u.id)

            db.session.add(msg)
            db.session.commit()

            msg = Message.query.filter_by(text="TEST_TEXT").one()

            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)

    def test_delete_message_logged_out(self):
        """Can a user delete a message?"""

        with self.client as c:
            
            msg = Message(text="TEST_TEXT", user_id=self.testuser.id)

            db.session.add(msg)
            db.session.commit()

            msg = Message.query.filter_by(text="TEST_TEXT").one()

            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", html)