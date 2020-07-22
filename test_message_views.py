"""Message View tests."""

import os
from unittest import TestCase

from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

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

    def tearDown(self):
        """Clean up any fouled transaction."""
        resp = super().tearDown()
        db.session.rollback()
        return resp
    
    def test_add_message(self):
        """Testing add message"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Hello"})

            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_authorized_show_message(self):
        """Show messages from authorized users"""
        
        msg = Message(
            id=2345,
            text="a test message",
            user_id=self.testuser.id
        )
        
        db.session.add(msg)
        db.session.commit()


        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
            msg = Message.query.get(2345)
            res = c.get(f'/messages/{msg.id}')
            
            self.assertEqual(res.status_code, 200)
            self.assertIn(msg.text, str(res.data))

    def test_message_delete(self):
        """ Test Delete Message for authorized users """

        msg = Message(id="8888", text="testing delete", user_id=self.testuser.id)

        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            msg = Message.query.filter(Message.text=="testing delete").first()

            resp = c.post(f'/messages/{msg.id}/delete', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            m = Message.query.get(8888)
            self.assertIsNone(m)     
