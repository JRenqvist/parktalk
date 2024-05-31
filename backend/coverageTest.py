import tempfile
import os
import pytest
import app as server
from app import app, db
import json
import base64
from datetime import timedelta


# Create new empty database
with app.app_context():
    db.drop_all()
    db.create_all()

@pytest.fixture()
def app():
    global db_fd, name
    db_fd, name = tempfile.mkstemp()
    server.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+str(name)
    server.app.config['TESTING'] = True
    server.app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
    
    with server.app.test_client() as client:
        with server.app.app_context():
            server.db.create_all()
        yield client
    os.close(db_fd)
    os.unlink(name)


@pytest.fixture()
def client(app):
    return server.app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


# Change 'url' to what is currently being tested
azure = "https://parktalk.azurewebsites.net"
local = "http://127.0.0.1:5000"
url = ""


def test_create_user(client):
    print("===== CREATE USER TESTS =====\n\n")

    # Create user John
    x = client.post(url+"/users/create", json={"username": "John",
                                                "email": "john@user.com",
                                                "password": "pass123"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Create user Jess
    x = client.post(url+"/users/create", json={"username": "Jess",
                                                "email": "jess@user.com",
                                                "password": "pass123"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Create user Jakob
    x = client.post(url+"/users/create", json={"username": "Jakob",
                                                "email": "jakob@user.com",
                                                "password": "pass123"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Create user Axel
    x = client.post(url+"/users/create", json={"username": "Axel",
                                                "email": "Axel@user.com",
                                                "password": "pass123"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Create user with username Jess
    x = client.post(url+"/users/create", json={"username": "Jess",
                                                "email": "newjess@user.com",
                                                "password": "pass123"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Create user with email jess@user.com
    x = client.post(url+"/users/create", json={"username": "NewJess",
                                                "email": "jess@user.com",
                                                "password": "pass123"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Create user with invalid email
    x = client.post(url+"/users/create", json={"username": "Jess",
                                                "email": "invalidemail",
                                                "password": "pass123"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Create another user with invalid email (no . after @)
    x = client.post(url+"/users/create", json={"username": "Jess",
                                                "email": "invalid@email",
                                                "password": "pass123"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # No JSON data
    x = client.post(url+"/users/create")
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Incorrect JSON data
    x = client.post(url+"/users/create", json={"username": "NewUser",
                                                "email": "",
                                                "password": "password123"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)


def test_user_login(client):
    global john_token, jess_token
    print("===== USER LOGIN TESTS =====\n\n")

    # John login
    x = client.post(url+"/users/login", json={"email": "john@user.com",
                                            "password": "pass123"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    john_token = x.json["token"]

    # Jess login
    x = client.post(url+"/users/login", json={"email": "jess@user.com",
                                            "password": "pass123"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    jess_token = x.json["token"]

    # login with incorrect email
    x = client.post(url+"/users/login", json={"email": "new@user.com",
                                            "password": "pass123"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # login with incorrect password
    x = client.post(url+"/users/login", json={"email": "jess@user.com",
                                            "password": "incorrect"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Incorrect JSON data
    x = client.post(url+"/users/login", json={"email": "a",
                                            "password": ""})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)
    
    # No JSON data
    x = client.post(url+"/users/login")
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)


def test_user_follow(client):
    print("===== USER FOLLOW TESTS =====\n\n")

    # John follows Jess
    x = client.post(url+"/users/follow",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"following_email": "jess@user.com",
                            "follower_email": "john@user.com"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Jess follows John
    x = client.post(url+"/users/follow",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"following_email": "john@user.com",
                            "follower_email": "jess@user.com"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # John follows John
    x = client.post(url+"/users/follow",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"following_email": "john@user.com",
                            "follower_email": "john@user.com"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Invalid email
    x = client.post(url+"/users/follow",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"following_email": "fake@email.com",
                            "follower_email": "john@user.com"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # No JSON data
    x = client.post(url+"/users/follow",
                      headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Missing header
    x = client.post(url+"/users/follow",
                      json={"following_email": "john@user.com",
                            "follower_email": "jess@user.com"})
    print(x.text)
    assert x.status_code == 401, print("Response code:", x.status_code)


def test_user_unfollow(client):
    print("===== USER UNFOLLOW TESTS =====\n\n")

    # John unfollows Jess
    x = client.delete(url+"/users/unfollow/jess@user.com/john@user.com",
                      headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # John unfollows John
    x = client.delete(url+"/users/unfollow/john@user.com/john@user.com",
                      headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Invalid email
    x = client.delete(url+"/users/unfollow/fake@user.com/john@user.com",
                      headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Invalid input
    x = client.delete(url+"/users/unfollow/fake@user.com/",
                      headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 404, print("Response code:", x.status_code)
    
    # Missing header
    x = client.delete(url+"/users/unfollow/john@user.com/jess@user.com")
    print(x.text)
    assert x.status_code == 401, print("Response code:", x.status_code)


def test_create_post(client):
    print("===== CREATE POST TESTS =====\n\n")

    # Normal post, id=1
    with open("testImages/1.jpg", "rb") as file:
        image_data = file.read()
    base64_image = base64.b64encode(image_data).decode("utf-8")
    data = {"email": "john@user.com",
            "caption": "Vad betyder denna skylt?",
            "address": "Sverige, Linköping",
            "picture": base64_image}
    x = client.post(url+"/posts/create",
                      headers={"Authorization": "Bearer " + john_token},
                      json=data)
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Normal post, id=2
    with open("testImages/2.jpg", "rb") as file:
        image_data = file.read()
    base64_image = base64.b64encode(image_data).decode("utf-8")
    data = {"email": "jess@user.com",
            "caption": "Fattar inte???",
            "address": "Sverige, Linköping",
            "picture": base64_image}
    x = client.post(url+"/posts/create",
                      headers={"Authorization": "Bearer " + jess_token},
                      json=data)
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # This post will be deleted. Used to see if related comments and likes gets removed correctly, id=3
    with open("testImages/3.jpg", "rb") as file:
        image_data = file.read()
    base64_image = base64.b64encode(image_data).decode("utf-8")
    data = {"email": "jess@user.com",
            "caption": "Denna post kommer bli raderad",
            "address": "Sverige, Linköping",
            "picture": base64_image}
    x = client.post(url+"/posts/create",
                      headers={"Authorization": "Bearer " + jess_token},
                      json=data)
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # This post will remain, but a comment on this post will be removed.
    # Used to see if related likes to comment gets removed correctly, id=4
    with open("testImages/4.jpeg", "rb") as file:
        image_data = file.read()
    base64_image = base64.b64encode(image_data).decode("utf-8")
    data = {"email": "john@user.com",
            "caption": "En kommentar kommer bli raderad under denna post",
            "address": "Sverige, Linköping",
            "picture": base64_image}
    x = client.post(url+"/posts/create",
                      headers={"Authorization": "Bearer " + john_token},
                      json=data)
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Invalid email
    with open("testImages/2.jpg", "rb") as file:
        image_data = file.read()
    base64_image = base64.b64encode(image_data).decode("utf-8")
    data = {"email": "fake@user.com",
            "caption": "Denna request ska inte läggas i databasen",
            "address": "Sverige, Linköping",
            "picture": base64_image}
    x = client.post(url+"/posts/create",
                      headers={"Authorization": "Bearer " + john_token},
                      json=data)
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)


def test_like_post(client):
    print("===== LIKE POST TESTS =====\n\n")

    # Normal like
    x = client.post(url+"/posts/like",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "post_id": "1"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Normal like
    x = client.post(url+"/posts/like",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"email": "john@user.com", "post_id": "2"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Like post that will be removed from database. Make sure relation also gets removed
    x = client.post(url+"/posts/like",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"email": "john@user.com", "post_id": "3"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Same person tries to like same post again
    x = client.post(url+"/posts/like",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "post_id": "1"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # User tries to like post that does not exist
    x = client.post(url+"/posts/like",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "post_id": "1000"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Fake email in json data
    x = client.post(url+"/posts/like",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "fake@user.com", "post_id": "1"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Try unliking post and then liking it again
    x = client.post(url+"/posts/unlike",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "post_id": "1"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    x = client.post(url+"/posts/like",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "post_id": "1"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)


def test_unlike_post(client):
    print("===== UNLIKE POST TESTS =====\n\n")

    # Normal unlike
    x = client.post(url+"/posts/unlike",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "post_id": "1"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Unlike post user has already unliked
    x = client.post(url+"/posts/unlike",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "post_id": "1"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # False email
    x = client.post(url+"/posts/unlike",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "fake@user.com", "post_id": "1"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Bad id
    x = client.post(url+"/posts/unlike",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "post_id": "1000"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)


def test_get_user_data(client):
    print("===== GET USER DATA TESTS =====\n\n")

    # Normal request
    x = client.get(url+"/users/get/data/john@user.com",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Normal request
    x = client.get(url+"/users/get/data/jess@user.com",
                     headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Invalid email
    x = client.get(url+"/users/get/data/fake@user.com",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Invalid input
    x = client.get(url+"/users/get/data/",
                     headers={"Authorization": "Bearer asdf"})
    print(x.text)
    assert x.status_code == 404, print("Response code:", x.status_code)

    # Invalid token
    x = client.get(url+"/users/get/data/john@user.com",
                     headers={"Authorization": "Bearer asdf"})
    print(x.text)
    assert x.status_code == 422, print("Response code:", x.status_code)


def test_get_feed_post(client):
    print("===== GET FEED POST TESTS =====\n\n")

    # Normal request
    x = client.get(url+"/feed/get",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Normal request
    x = client.get(url+"/feed/get",
                     headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Bad token
    x = client.get(url+"/feed/get",
                     headers={"Authorization": "Bearer asdf"})
    print(x.text)
    assert x.status_code == 422, print("Response code:", x.status_code)


def test_get_is_following(client):
    print("===== GET IS FOLLOWING TESTS =====\n\n")

    # Normal request
    x = client.get(url+"/users/isfollowing/jess@user.com/john@user.com",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    correct_response = json.loads("""{"status": "success", "message": "true"}""")
    assert x.json == correct_response, print("Response text:", x.text)

    # Normal request
    x = client.get(url+"/users/isfollowing/john@user.com/jess@user.com",
                     headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    correct_response = json.loads("""{"status": "success", "message": "false"}""")
    assert x.json == correct_response, print("Response text:", x.text)

    # Invalid email
    x = client.get(url+"/users/isfollowing/fake@user.com/john@user.com",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Invalid input
    x = client.get(url+"/users/isfollowing/",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 404, print("Response code:", x.status_code)

    # Bad token
    x = client.get(url+"/users/isfollowing/john@user.com/jess@user.com",
                     headers={"Authorization": "Bearer asdf"})
    print(x.text)
    assert x.status_code == 422, print("Response code:", x.status_code)


def test_get_following_feed(client):
    print("===== GET FOLLOWING FEED TESTS =====\n\n")

    # Normal request
    x = client.get(url+"/feed/get/following/jess@user.com",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # John tries to get followers feed. John isn't following anyone when this function is called.
    x = client.get(url+"/feed/get/following/john@user.com",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 404, print("Response code:", x.status_code)

    # Bad email
    x = client.get(url+"/feed/get/following/fake@user.com",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # No email
    x = client.get(url+"/feed/get/following/",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 404, print("Response code:", x.status_code)

    # Bad token
    x = client.get(url+"/feed/get/following/jess@user.com",
                     headers={"Authorization": "Bearer asdf"})
    print(x.text)
    assert x.status_code == 422, print("Response code:", x.status_code)



def test_get_user_posts(client):
    print("===== GET USER POSTS TESTS =====\n\n")

    # Normal request
    x = client.get(url+"/users/get/posts/jess@user.com",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Normal request
    x = client.get(url+"/users/get/posts/john@user.com",
                     headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Invalid email
    x = client.get(url+"/users/get/posts/fake@user.com",
                     headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Invalid token
    x = client.get(url+"/users/get/posts/john@user.com",
                     headers={"Authorization": "Bearer asdf"})
    print(x.text)
    assert x.status_code == 422, print("Response code:", x.status_code)


def test_get_user_comments(client):
    print("===== GET USER COMMENTS TESTS =====\n\n")
    
    # Normal request
    x = client.get(url+"/users/get/comments/john@user.com",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Normal request
    x = client.get(url+"/users/get/comments/jess@user.com",
                     headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Invalid email
    x = client.get(url+"/users/get/comments/fake@user.com",
                     headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Invalid token
    x = client.get(url+"/users/get/comments/jess@user.com",
                     headers={"Authorization": "Bearer asdf"})
    print(x.text)
    assert x.status_code == 422, print("Response code:", x.status_code)


def test_get_leaderboard(client):
    print("===== GET LEADERBOARD TESTS =====\n\n")

    # Normal request
    x = client.get(url+"/users/get/leaderboard",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Bad token
    x = client.get(url+"/users/get/leaderboard",
                     headers={"Authorization": "Bearer asdf"})
    print(x.text)
    assert x.status_code == 422, print("Response code:", x.status_code)


def test_get_post(client):
    print("===== GET POST TESTS =====\n\n")
    
    # Normal request
    x = client.get(url+"/posts/get/1",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Invalid post id
    x = client.get(url+"/posts/get/100",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Invalid token
    x = client.get(url+"/posts/get/1",
                     headers={"Authorization": "Bearer asdf"})
    print(x.text)
    assert x.status_code == 422, print("Response code:", x.status_code)


def test_create_comment(client):
    print("===== ADD COMMENT TESTS =====\n\n")

    # Normal comment, id=1
    x = client.post(url+"/posts/comments/add",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "post_id": "1",
                            "comment": "Jess' comment on John's post"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    
    # Normal comment, id=2
    x = client.post(url+"/posts/comments/add",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"email": "john@user.com", "post_id": "2",
                            "comment": "John's comment on Jess' post"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Normal comment, id=3
    x = client.post(url+"/posts/comments/add",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"email": "john@user.com", "post_id": "2",
                            "comment": "John's 2nd comment on Jess' post"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Comment on post that will be removed from database. Make sure relation is removed correctly, id=4
    x = client.post(url+"/posts/comments/add",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"email": "john@user.com", "post_id": "3",
                            "comment": "This comment should be removed after the post is deleted"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # This comment will be removed but not the post. Make sure relation is removed correctly, id=5
    x = client.post(url+"/posts/comments/add",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"email": "john@user.com", "post_id": "4",
                            "comment": "This comment should be removed after the post is deleted"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Invalid email
    x = client.post(url+"/posts/comments/add",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"email": "fake@user.com", "post_id": "2",
                            "comment": "Fake email address"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Invalid post_id
    x = client.post(url+"/posts/comments/add",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"email": "jess@user.com", "post_id": "1000",
                            "comment": "Invalid post_id"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)


def test_like_comment(client):
    print("===== LIKE COMMENT TESTS =====\n\n")

    # Normal like, id=1
    x = client.post(url+"/posts/comments/like",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "comment_id": "1"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Normal like, id=2
    x = client.post(url+"/posts/comments/like",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"email": "john@user.com", "comment_id": "2"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Like comment on post that will be removed, id=3
    x = client.post(url+"/posts/comments/like",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "comment_id": "4"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Like comment that will be removed, id=4
    x = client.post(url+"/posts/comments/like",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"email": "john@user.com", "comment_id": "5"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Same person tries to like same post again
    x = client.post(url+"/posts/comments/like",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "comment_id": "1"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # User tries to like post that does not exist
    x = client.post(url+"/posts/comments/like",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "comment_id": "1000"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Fake email in json data
    x = client.post(url+"/posts/comments/like",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "fake@user.com", "comment_id": "1"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Try unliking comment and then liking it again
    x = client.post(url+"/posts/comments/unlike",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "comment_id": "1"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    x = client.post(url+"/posts/comments/like",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "comment_id": "1"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)


def test_delete_post(client):
    print("===== DELETE POST TESTS =====\n\n")

    # Invalid email
    x = client.delete(url+"/posts/delete/fake@user.com/3",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Another user tries to delete someone else's post
    x = client.delete(url+"/posts/delete/john@user.com/3",
                      headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Correct delete request
    x = client.delete(url+"/posts/delete/jess@user.com/3",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)


def test_unlike_comment(client):
    print("===== UNLIKE COMMENTS TESTS =====\n\n")

    # Normal unlike
    x = client.post(url+"/posts/comments/unlike",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "comment_id": "1"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Unlike post user has already unliked
    x = client.post(url+"/posts/comments/unlike",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "comment_id": "1"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # False email
    x = client.post(url+"/posts/comments/unlike",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "fake@user.com", "comment_id": "1"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Bad id
    x = client.post(url+"/posts/comments/unlike",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "comment_id": "1000"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)


def test_delete_comment(client):
    print("===== DELETE COMMENT TESTS =====\n\n")

    # Invalid email
    x = client.delete(url+"/posts/comments/delete/fake@user.com/3",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Another user tries to delete someone else's comment
    x = client.delete(url+"/posts/comments/delete/jess@user.com/3",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Correct delete request
    x = client.delete(url+"/posts/comments/delete/john@user.com/3",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Delete comment with like. This should also delete the like from the database
    x = client.delete(url+"/posts/comments/delete/john@user.com/5",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)


def test_is_post_liked(client):
    print("===== CHECK IF POST IS LIKED =====\n\n")

    # Invalid email
    x = client.get(url+"/posts/ispostliked/fake@user.com/3",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # correct request
    x = client.get(url+"/posts/ispostliked/john@user.com/2",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Invalid post_id
    x = client.get(url+"/posts/ispostliked/john@user.com/999",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Invalid input
    x = client.get(url+"/posts/ispostliked/john@user.com/",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 404, print("Response code:", x.status_code)


def test_is_comment_liked(client):
    print("===== CHECK IF COMMENT IS LIKED =====\n\n")
    
        # Invalid email
    x = client.get(url+"/posts/iscommentliked/fake@user.com/3",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # correct request
    x = client.get(url+"/posts/iscommentliked/jess@user.com/1",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)


def test_is_user_owner_of_post(client):
    print("===== CHECK IF USER IS OWNER OF POST =====\n\n")
    
    # Normal request
    x = client.get(url+"/posts/isuserowner/john@user.com/1",
                      headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    correct_response = json.loads("""{"status": "success", "message": "true"}""")
    assert x.json == correct_response, print("Response text:", x.text)

    # Normal request
    x = client.get(url+"/posts/isuserowner/jess@user.com/2",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    correct_response = json.loads("""{"status": "success", "message": "true"}""")
    assert x.json == correct_response, print("Response text:", x.text)

    # User is not owner of post
    x = client.get(url+"/posts/isuserowner/john@user.com/2",
                      headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    correct_response = json.loads("""{"status": "success", "message": "false"}""")
    assert x.json == correct_response, print("Response text:", x.text)

    # Invalid email
    x = client.get(url+"/posts/isuserowner/fake@user.com/2",
                      headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)


def test_get_users_from_search(client):
    print("===== GET USERS FROM SEARCH =====\n\n")
    
    # Normal request
    x = client.get(url+"/users/search/john",
                      headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Normal request
    x = client.get(url+"/users/search/j",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Normal request
    x = client.get(url+"/users/search/a",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Bad token
    x = client.get(url+"/users/search/john",
                      headers={"Authorization": "Bearer asdf"})
    print(x.text)
    assert x.status_code == 422, print("Response code:", x.status_code)


def test_is_user_owner_of_comment(client):
    print("===== CHECK IF USER IS OWNER OF COMMENT =====\n\n")

    # Normal request
    x = client.get(url+"/posts/comments/isuserowner/jess@user.com/1",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    correct_response = json.loads("""{"status": "success", "message": "true"}""")
    assert x.json == correct_response, print("Response text:", x.text)

    # Normal request
    x = client.get(url+"/posts/comments/isuserowner/john@user.com/2",
                      headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    correct_response = json.loads("""{"status": "success", "message": "true"}""")
    assert x.json == correct_response, print("Response text:", x.text)

    # User is not owner of comment
    x = client.get(url+"/posts/comments/isuserowner/jess@user.com/2",
                    headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    correct_response = json.loads("""{"status": "success", "message": "false"}""")
    assert x.json == correct_response, print("Response text:", x.text)

    # Invalid email
    x = client.get(url+"/posts/comments/isuserowner/fake@user.com/2",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)


def test_get_comments_on_post(client):
    print("===== GET COMMENTS ON POST TESTS =====\n\n")

    # Normal request
    x = client.get(url+"/posts/comments/get/2",
                     headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Invalid post_id
    x = client.get(url+"/posts/comments/get/999",
                     headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)


def test_user_logout(client):
    print("===== USER LOGOUT TESTS =====\n\n")
    
    # John logout
    x = client.post(url+"/users/logout", headers={"Authorization":
                                                   "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Jess logout
    x = client.post(url+"/users/logout", headers={"Authorization":
                                                   "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Send request without headers
    x = client.post(url+"/users/logout")
    print(x.text)
    assert x.status_code == 401, print("Response code:", x.status_code)

    # Send incorrect header
    x = client.post(url+"/users/logout", headers={"Authorization":
                                                   "Bearer asdf"})
    print(x.text)
    assert x.status_code == 422, print("Response code:", x.status_code)
