"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

import os
from unittest import TestCase
from sqlalchemy import exc

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

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        u1 = User.signup("testuser1","test1@test.com","password",None)
        uid_1 =1001
        u1.id = uid_1

        u2 = User.signup("testuser2", "test2@test.com", "password2", None)
        uid_2 = 2002
        u2.id = uid_2
        
        db.session.commit()

        u1 = User.query.get(uid_1)
        u2 = User.query.get(uid_2)
        self.u1 = u1
        self.uid_1 = uid_1

        self.u2 = u2
        self.uid_2 = uid_2

    def tearDown(self):
        db.session.rollback()
        

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    
    ### signup tests - valid & Invalid Username,pwd,email ######

    def test_valid_signup(self):
        usr_test = User.signup("testusr1","testusr1@email.com","testusr_pwd",None)
        usr_id = 90000
        usr_test.id = usr_id
        db.session.commit()

        usr_test = User.query.get(usr_id)
        self.assertIsNotNone(usr_test)
        self.assertEqual(usr_test.username,"testusr1")
        self.assertEqual(usr_test.email, "testusr1@email.com")
        self.assertNotEqual(usr_test.password,"testusr_pwd")
        #Bcyrpt string password validation - should start with $2b$
        self.assertTrue(usr_test.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        invalid_user = User.signup(None,"invalid_usr@email.com","password",None)
        uid = 9876543
        invalid_user.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid_user = User.signup("testusr4",None,"password",None)
        uid = 4567890
        invalid_user.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("tester","mail@mail.com",None,None)

        with self.assertRaises(ValueError) as context:
            User.signup("tester","mail@mail.com","",None)
    
    ##### Authentication tests ##############

    def test_valid_authentication(self):
        u = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid_1)
    
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "badpassword"))

    #### Followers, Following tests ########

    def test_user_follows(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u2.following), 0)
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u1.following), 1)

        self.assertEqual(self.u2.followers[0].id, self.u1.id)
        self.assertEqual(self.u1.following[0].id, self.u2.id)

    def test_is_following(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_followed_by(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))
