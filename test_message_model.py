"""Message model tests."""

import os
from unittest import TestCase
from models import Likes, db, connect_db, User, Message

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()

class MessageModelTestCase(TestCase):
    """Test cases for Message Model"""

    def setUp(self):
        """Create test client, add sample data."""

        Message.query.delete()
        User.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        
        db.session.commit()

        self.testmessage = Message(
            text="TEST_TEXT",
            user_id=self.testuser.id
        )

        db.session.add(self.testmessage)
        db.session.commit()
    
    def test_message_model(self):
        """Does basic model work?"""

        m = Message(
            text="testmessage_content",
            user_id=self.testuser.id
        )

        db.session.add(m)
        db.session.commit()

        self.assertEqual(len(self.testuser.messages), 2)

    def test_message_repr(self):
        """Test model __repr__ method"""
        
        self.assertEqual(self.testmessage.__repr__(), f"<Message {self.testmessage.id} user:{self.testmessage.user_id} >")

    def test_message_like(self):
        """Test is_liked, like, and unlike methods"""

        Message.like(self.testuser.id, self.testmessage.id)

        self.assertTrue(Likes.query.filter_by(user_id=self.testuser.id).first())
        self.assertTrue(self.testmessage.is_liked_by(self.testuser.id))

        Message.unlike(self.testuser.id, self.testmessage.id)

        self.assertFalse(Likes.query.filter_by(user_id=self.testuser.id).first())
        self.assertFalse(self.testmessage.is_liked_by(self.testuser.id))