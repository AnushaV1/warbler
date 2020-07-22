"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()
class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        """Create test client, add sample data."""
        self.u1 = User.signup(
                email="user1@test.com",
                username="testuser1",
                password="password",
                image_url = None
            )
        self.u2 = User.signup(
                email="user2@test.com",
                username="testuser2",
                password="password",
                image_url = None
            )
        db.session.commit()
        self.client = app.test_client()

    def teardown(self):
        """Clean up after each test"""
        db.session.rollback()

    def test_message_model(self):
        """Test message model"""
        # create new messages for both users
        msg = Message(text="Testing message", user_id=self.u1.id)
        msg2 = Message(text="Testing second message", user_id=self.u2.id)
        db.session.add_all([msg,msg2])
        db.session.commit()

        self.assertEqual(len(self.u1.messages), 1)
        self.assertIn(msg, self.u1.messages) 
        self.assertEqual(self.u1.messages[0].text, "Testing message")
        self.assertIn(msg2, self.u2.messages) 
        self.assertEqual(len(self.u2.messages), 1)
        self.assertEqual(self.u2.messages[0].text, "Testing second message")

    def test_add_message(self):
        """Check to see if messages can be added"""
        # create new messages for both users
        msg1 = Message(text='Test new message1', user_id=self.u1.id)
        msg2 = Message(text='Test new message2', user_id=self.u2.id)
        db.session.commit()

        # add messages
        self.u1.messages.append(msg1) 
        self.u2.messages.append(msg2)
        self.assertIn(msg1, self.u1.messages)
        self.assertIn(msg2, self.u2.messages)

    def test_message_likes(self):
        m1 = Message(text="a new warble", user_id=self.u1.id)
        m2 = Message(text="an informative warble",user_id=self.u2.id)
        db.session.commit()

        self.u1.likes.append(m2)
        self.u2.likes.append(m1) 
        self.assertIn(m2, self.u1.likes)
        self.assertIn(m1, self.u2.likes) 
