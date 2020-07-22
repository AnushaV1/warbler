"""User view tests."""

import os
from unittest import TestCase

from models import db, connect_db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for users."""
    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        self.u1  = User.signup("testuser1","test1@test.com","password",None)
        self.uid_1 =10001
        self.u1.id = self.uid_1

        self.u2 = User.signup("testuser2", "test2@test.com", "password2", None)
        self.uid_2 = 20002
        self.u2.id = self.uid_2

        self.u3 = User.signup("user3","user3@test.com","password",None)
        self.uid_3 =30003
        self.u3.id = self.uid_3

        self.u4 = User.signup("user4","user4@test.com","password",None)
        self.uid_4 =30004
        self.u4.id = self.uid_4
        db.session.commit()


        
        f1 = self.u1.following.append(self.u2)
        f2 = self.u2.following.append(self.u1)
        f3 = self.u3.following.append(self.u1)

        db.session.commit()

        
        self.msg = Message(id=7777, text='Test Message', user_id=self.u2.id)
        db.session.add(self.msg)
        db.session.commit()

        self.MSG = "MSG"


    def tearDown(self):
        """Clean up any fouled transaction."""
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_signup(self):
        """Test Sign Up root route"""
        with self.client as client:
            res = client.get('/')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("<h1>What's Happening?</h1>", html)
            self.assertIn("<h4>New to Warbler?</h4>", html)

    def test_login(self):
        """Check login route"""
        with self.client as client:
            
            res = client.get('/login')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h2 class="join-message">Welcome back.</h2>', html)

    def test_logout(self):
        """Check logout route"""
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            res = client.get("/logout")
            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, 'http://localhost/login')

    def test_users_list(self):
        """ check the homepage route """
        with app.test_client() as client:
            response = client.get('/users')
            html = response.get_data(as_text = True)

            self.assertEqual(response.status_code, 200)
            self.assertIn("@testuser1", str(response.data))
            self.assertIn("@testuser2", str(response.data))
            

    def test_show_user(self):
        """ Test show user details """
        with app.test_client() as client:
            response = client.get(f"/users/{self.uid_1}")
            html = response.get_data(as_text = True)

            self.assertEqual(response.status_code, 200)
            self.assertIn("@testuser1", str(response.data))


    
    def test_search_users(self):
        with self.client as c:
            resp = c.get("/users?q=test")

            self.assertIn("@testuser1", str(resp.data))
            self.assertIn("@testuser2", str(resp.data))            

            self.assertNotIn("@user3", str(resp.data))
            self.assertNotIn("@user4", str(resp.data))
        
    
    def test_show_user_following(self):
        """Check user following route"""
        
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            res = client.get(f"/users/{self.u1.id}/followers")
            self.assertEqual(res.status_code, 200)
            self.assertIn("@testuser1", str(res.data))
            
            
        with self.client as client:
            res = client.get(f"users/{self.u1.id}/followers")
            self.assertLessEqual(res.status_code, 302)
            self.assertIn("@testuser1", str(res.data))

    def test_show_user_followers(self):
        """Check user followers route"""
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
            res = client.get(f'users/{self.uid_1}/followers')

            self.assertEqual(res.status_code, 200)
            self.assertIn("@testuser1", str(res.data))


    def test_show_follow_user(self):
        """Check route when you follow a user"""
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
            res = client.post(f'users/follow/{self.u1.id}')

            
            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, f'http://localhost/users/{self.uid_1}/following')

    def test_show_add_like(self):
        """Show route when message is likes"""
        with self.client as client:
            id = self.msg.id
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            res = client.post("/messages/7777/like", follow_redirects=True)
            self.assertEqual(res.status_code, 200)


    def test_show_remove_like(self):
        """Show route when message is disliked"""
        
        msg = Message.query.filter(Message.text=="Test Message").one()
        self.assertIsNotNone(msg)
        self.assertNotEqual(msg.user_id, self.u1.id)

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            resp = client.post(f"/messages/{msg.id}/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)