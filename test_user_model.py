"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os, pdb
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()
        self.user = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(self.user)
        db.session.commit()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(u.email, "test1@test.com")
        self.assertEqual(u.username, "testuser1")
    
    def test_user_repr(self):
        """Does the repr method work?"""

        self.assertEqual(self.user.__repr__(),
            f"<User #{self.user.id}: {self.user.username}, {self.user.email}>")
    
    def test_user_follows(self):
        """Do the is_following and is_followed_by methods work?"""

        u = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        follow = Follows(
            user_being_followed_id=u.id,
            user_following_id=self.user.id
        )

        db.session.add(follow)
        db.session.commit()

        self.assertTrue(u.is_followed_by(self.user))
        self.assertFalse(self.user.is_followed_by(u))
        self.assertTrue(self.user.is_following(u))
        self.assertFalse(u.is_following(self.user))

    def test_user_signup(self):
        """Does the signup method work?"""

        new_user = User.signup("testuser1", "test1@test.com", "PASSWORD", "")

        self.assertIsInstance(new_user, User)
        self.assertEqual(User.query.filter_by(username="testuser1").one(), new_user)

    def test_user_authentication(self):
        """Does the authenticate method work?"""

        User.signup("testuser1", "test1@test.com", "PASSWORD", "")

        authenticated = User.authenticate("testuser1", "PASSWORD")

        self.assertTrue(authenticated)
        self.assertIsInstance(authenticated, User)
        self.assertFalse(User.authenticate("blabla", "blabla"))
        self.assertFalse(User.authenticate("testuser1", "wrong_pwd"))