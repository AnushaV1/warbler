"""User view tests."""

# run these tests like:
#
#    python -m unittest test_user_view.py

import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY, g

app.config['WTF_CSRF_ENABLED'] = False
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """ clear tables and add sample use  """
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add_all([user, post, tag])
        db.session.commit()

        self.post_id = post.id
        self.user_id = user.id
        self.tag_id = tag.id

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_users_list(self):
        """ check the homepage route """
        with app.test_client() as client:
            response = client.get('/users')
            html = response.get_data(as_text = True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('user_firstname', html)

    def test_show_user(self):
        """ Test show user details """
        with app.test_client() as client:
            response = client.get(f"/users/{self.user_id}")
            html = response.get_data(as_text = True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('<p>user_firstname user_lastname</p>', html)
