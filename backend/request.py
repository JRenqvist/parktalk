import requests
import base64
import json
import time

# Change 'url' to what is currently being tested
azure = "https://parktalk.azurewebsites.net"
local = "http://127.0.0.1:5000"
url = local


def test_create_user():
    print("===== CREATE USER TESTS =====\n\n")

    # Create user John
    x = requests.post(url+"/users/create", json={"username": "John",
                                                "email": "john@user.com",
                                                "password": "pass123"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Create user Jess
    x = requests.post(url+"/users/create", json={"username": "Jess",
                                                "email": "jess@user.com",
                                                "password": "pass123"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Create user Jakob
    x = requests.post(url+"/users/create", json={"username": "Jakob",
                                                "email": "jakob@user.com",
                                                "password": "pass123"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Create user Axel
    x = requests.post(url+"/users/create", json={"username": "Axel",
                                                "email": "Axel@user.com",
                                                "password": "pass123"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Create user with username Jess
    x = requests.post(url+"/users/create", json={"username": "Jess",
                                                "email": "newjess@user.com",
                                                "password": "pass123"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Create user with email jess@user.com
    x = requests.post(url+"/users/create", json={"username": "NewJess",
                                                "email": "jess@user.com",
                                                "password": "pass123"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Create user with invalid email
    x = requests.post(url+"/users/create", json={"username": "Jess",
                                                "email": "invalidemail",
                                                "password": "pass123"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Create another user with invalid email (no . after @)
    x = requests.post(url+"/users/create", json={"username": "Jess",
                                                "email": "invalid@email",
                                                "password": "pass123"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # No JSON data
    x = requests.post(url+"/users/create")
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Incorrect JSON data
    x = requests.post(url+"/users/create", json={"username": "NewUser",
                                                "email": "",
                                                "password": "password123"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)


def test_user_login():
    global john_token, jess_token
    print("===== USER LOGIN TESTS =====\n\n")

    # John login
    x = requests.post(url+"/users/login", json={"email": "john@user.com",
                                            "password": "pass123"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    john_token = x.json()["token"]

    # Jess login
    x = requests.post(url+"/users/login", json={"email": "jess@user.com",
                                            "password": "pass123"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    jess_token = x.json()["token"]

    # login with incorrect email
    x = requests.post(url+"/users/login", json={"email": "new@user.com",
                                            "password": "pass123"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # login with incorrect password
    x = requests.post(url+"/users/login", json={"email": "jess@user.com",
                                            "password": "incorrect"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Incorrect JSON data
    x = requests.post(url+"/users/login", json={"email": "a",
                                            "password": ""})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)
    
    # No JSON data
    x = requests.post(url+"/users/login")
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)


def test_user_logout():
    print("===== USER LOGOUT TESTS =====\n\n")
    
    # John logout
    x = requests.post(url+"/users/logout", headers={"Authorization":
                                                   "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Jess logout
    x = requests.post(url+"/users/logout", headers={"Authorization":
                                                   "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Send request without headers
    x = requests.post(url+"/users/logout")
    print(x.text)
    assert x.status_code == 401, print("Response code:", x.status_code)

    # Send incorrect header
    x = requests.post(url+"/users/logout", headers={"Authorization":
                                                   "Bearer asdf"})
    print(x.text)
    assert x.status_code == 422, print("Response code:", x.status_code)


def test_user_follow():
    print("===== USER FOLLOW TESTS =====\n\n")

    # John follows Jess
    x = requests.post(url+"/users/follow",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"following_email": "jess@user.com",
                            "follower_email": "john@user.com"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Jess follows John
    x = requests.post(url+"/users/follow",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"following_email": "john@user.com",
                            "follower_email": "jess@user.com"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # John follows John
    x = requests.post(url+"/users/follow",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"following_email": "john@user.com",
                            "follower_email": "john@user.com"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Invalid email
    x = requests.post(url+"/users/follow",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"following_email": "fake@email.com",
                            "follower_email": "john@user.com"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # No JSON data
    x = requests.post(url+"/users/follow",
                      headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Missing header
    x = requests.post(url+"/users/follow",
                      json={"following_email": "john@user.com",
                            "follower_email": "jess@user.com"})
    print(x.text)
    assert x.status_code == 401, print("Response code:", x.status_code)


def test_user_unfollow():
    print("===== USER UNFOLLOW TESTS =====\n\n")

    # John unfollows Jess
    x = requests.delete(url+"/users/unfollow/jess@user.com/john@user.com",
                      headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # John unfollows John
    x = requests.delete(url+"/users/unfollow/john@user.com/john@user.com",
                      headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Invalid email
    x = requests.delete(url+"/users/unfollow/fake@user.com/john@user.com",
                      headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Invalid input
    x = requests.delete(url+"/users/unfollow/fake@user.com/",
                      headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 404, print("Response code:", x.status_code)
    
    # Missing header
    x = requests.delete(url+"/users/unfollow/john@user.com/jess@user.com")
    print(x.text)
    assert x.status_code == 401, print("Response code:", x.status_code)


def test_create_post():
    print("===== CREATE POST TESTS =====\n\n")

    # Normal post, id=1
    with open("testImages/1.jpg", "rb") as file:
        image_data = file.read()
    base64_image = base64.b64encode(image_data).decode("utf-8")
    data = {"email": "john@user.com",
            "caption": "Vad betyder denna skylt?",
            "address": "Sverige, Linköping",
            "picture": base64_image}
    x = requests.post(url+"/posts/create",
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
    x = requests.post(url+"/posts/create",
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
    x = requests.post(url+"/posts/create",
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
    x = requests.post(url+"/posts/create",
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
    x = requests.post(url+"/posts/create",
                      headers={"Authorization": "Bearer " + john_token},
                      json=data)
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)


def test_like_post():
    print("===== LIKE POST TESTS =====\n\n")

    # Normal like
    x = requests.post(url+"/posts/like",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "post_id": "1"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Normal like
    x = requests.post(url+"/posts/like",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"email": "john@user.com", "post_id": "2"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Like post that will be removed from database. Make sure relation also gets removed
    x = requests.post(url+"/posts/like",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"email": "john@user.com", "post_id": "3"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Same person tries to like same post again
    x = requests.post(url+"/posts/like",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "post_id": "1"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # User tries to like post that does not exist
    x = requests.post(url+"/posts/like",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "post_id": "1000"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Fake email in json data
    x = requests.post(url+"/posts/like",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "fake@user.com", "post_id": "1"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Try unliking post and then liking it again
    x = requests.post(url+"/posts/unlike",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "post_id": "1"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    x = requests.post(url+"/posts/like",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "post_id": "1"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)


def test_unlike_post():
    print("===== UNLIKE POST TESTS =====\n\n")

    # Normal unlike
    x = requests.post(url+"/posts/unlike",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "post_id": "1"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Unlike post user has already unliked
    x = requests.post(url+"/posts/unlike",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "post_id": "1"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # False email
    x = requests.post(url+"/posts/unlike",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "fake@user.com", "post_id": "1"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Bad id
    x = requests.post(url+"/posts/unlike",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "post_id": "1000"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)


def test_delete_post():
    print("===== DELETE POST TESTS =====\n\n")

    # Invalid email
    x = requests.delete(url+"/posts/delete/fake@user.com/3",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Another user tries to delete someone else's post
    x = requests.delete(url+"/posts/delete/john@user.com/3",
                      headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Correct delete request
    x = requests.delete(url+"/posts/delete/jess@user.com/3",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)


def test_get_user_data():
    print("===== GET USER DATA TESTS =====\n\n")

    # Normal request
    x = requests.get(url+"/users/get/data/john@user.com",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Normal request
    x = requests.get(url+"/users/get/data/jess@user.com",
                     headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Invalid email
    x = requests.get(url+"/users/get/data/fake@user.com",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Invalid input
    x = requests.get(url+"/users/get/data/",
                     headers={"Authorization": "Bearer asdf"})
    print(x.text)
    assert x.status_code == 404, print("Response code:", x.status_code)

    # Invalid token
    x = requests.get(url+"/users/get/data/john@user.com",
                     headers={"Authorization": "Bearer asdf"})
    print(x.text)
    assert x.status_code == 422, print("Response code:", x.status_code)


def test_get_feed_post():
    print("===== GET FEED POST TESTS =====\n\n")

    # Normal request
    x = requests.get(url+"/feed/get",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Normal request
    x = requests.get(url+"/feed/get",
                     headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Bad token
    x = requests.get(url+"/feed/get",
                     headers={"Authorization": "Bearer asdf"})
    print(x.text)
    assert x.status_code == 422, print("Response code:", x.status_code)


def test_get_is_following():
    print("===== GET IS FOLLOWING TESTS =====\n\n")

    # Normal request
    x = requests.get(url+"/users/isfollowing/jess@user.com/john@user.com",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    correct_response = json.loads("""{"status": "success", "message": "true"}""")
    assert x.json() == correct_response, print("Response text:", x.text)

    # Normal request
    x = requests.get(url+"/users/isfollowing/john@user.com/jess@user.com",
                     headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    correct_response = json.loads("""{"status": "success", "message": "false"}""")
    assert x.json() == correct_response, print("Response text:", x.text)

    # Invalid email
    x = requests.get(url+"/users/isfollowing/fake@user.com/john@user.com",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Invalid input
    x = requests.get(url+"/users/isfollowing/",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 404, print("Response code:", x.status_code)

    # Bad token
    x = requests.get(url+"/users/isfollowing/john@user.com/jess@user.com",
                     headers={"Authorization": "Bearer asdf"})
    print(x.text)
    assert x.status_code == 422, print("Response code:", x.status_code)


def test_get_following_feed():
    print("===== GET FOLLOWING FEED TESTS =====\n\n")

    # Normal request
    x = requests.get(url+"/feed/get/following/jess@user.com",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # John tries to get followers feed. John isn't following anyone when this function is called.
    x = requests.get(url+"/feed/get/following/john@user.com",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 404, print("Response code:", x.status_code)

    # Bad email
    x = requests.get(url+"/feed/get/following/fake@user.com",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # No email
    x = requests.get(url+"/feed/get/following/",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 404, print("Response code:", x.status_code)

    # Bad token
    x = requests.get(url+"/feed/get/following/jess@user.com",
                     headers={"Authorization": "Bearer asdf"})
    print(x.text)
    assert x.status_code == 422, print("Response code:", x.status_code)



def test_get_user_posts():
    print("===== GET USER POSTS TESTS =====\n\n")

    # Normal request
    x = requests.get(url+"/users/get/posts/jess@user.com",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Normal request
    x = requests.get(url+"/users/get/posts/john@user.com",
                     headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Invalid email
    x = requests.get(url+"/users/get/posts/fake@user.com",
                     headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Invalid token
    x = requests.get(url+"/users/get/posts/john@user.com",
                     headers={"Authorization": "Bearer asdf"})
    print(x.text)
    assert x.status_code == 422, print("Response code:", x.status_code)


def test_get_user_comments():
    print("===== GET USER COMMENTS TESTS =====\n\n")
    
    # Normal request
    x = requests.get(url+"/users/get/comments/john@user.com",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Normal request
    x = requests.get(url+"/users/get/comments/jess@user.com",
                     headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Invalid email
    x = requests.get(url+"/users/get/comments/fake@user.com",
                     headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Invalid token
    x = requests.get(url+"/users/get/comments/jess@user.com",
                     headers={"Authorization": "Bearer asdf"})
    print(x.text)
    assert x.status_code == 422, print("Response code:", x.status_code)


def test_get_leaderboard():
    print("===== GET LEADERBOARD TESTS =====\n\n")

    # Normal request
    x = requests.get(url+"/users/get/leaderboard",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Bad token
    x = requests.get(url+"/users/get/leaderboard",
                     headers={"Authorization": "Bearer asdf"})
    print(x.text)
    assert x.status_code == 422, print("Response code:", x.status_code)


def test_get_post():
    print("===== GET POST TESTS =====\n\n")
    
    # Normal request
    x = requests.get(url+"/posts/get/1",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Invalid post id
    x = requests.get(url+"/posts/get/100",
                     headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Invalid token
    x = requests.get(url+"/posts/get/1",
                     headers={"Authorization": "Bearer asdf"})
    print(x.text)
    assert x.status_code == 422, print("Response code:", x.status_code)


def test_create_comment():
    print("===== ADD COMMENT TESTS =====\n\n")

    # Normal comment, id=1
    x = requests.post(url+"/posts/comments/add",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "post_id": "1",
                            "comment": "Jess' comment on John's post"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    
    # Normal comment, id=2
    x = requests.post(url+"/posts/comments/add",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"email": "john@user.com", "post_id": "2",
                            "comment": "John's comment on Jess' post"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Normal comment, id=3
    x = requests.post(url+"/posts/comments/add",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"email": "john@user.com", "post_id": "2",
                            "comment": "John's 2nd comment on Jess' post"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Comment on post that will be removed from database. Make sure relation is removed correctly, id=4
    x = requests.post(url+"/posts/comments/add",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"email": "john@user.com", "post_id": "3",
                            "comment": "This comment should be removed after the post is deleted"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # This comment will be removed but not the post. Make sure relation is removed correctly, id=5
    x = requests.post(url+"/posts/comments/add",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"email": "john@user.com", "post_id": "4",
                            "comment": "This comment should be removed after the post is deleted"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Invalid email
    x = requests.post(url+"/posts/comments/add",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"email": "fake@user.com", "post_id": "2",
                            "comment": "Fake email address"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Invalid post_id
    x = requests.post(url+"/posts/comments/add",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"email": "jess@user.com", "post_id": "1000",
                            "comment": "Invalid post_id"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)


def test_like_comment():
    print("===== LIKE COMMENT TESTS =====\n\n")

    # Normal like, id=1
    x = requests.post(url+"/posts/comments/like",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "comment_id": "1"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Normal like, id=2
    x = requests.post(url+"/posts/comments/like",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"email": "john@user.com", "comment_id": "2"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Like comment on post that will be removed, id=3
    x = requests.post(url+"/posts/comments/like",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "comment_id": "4"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Like comment that will be removed, id=4
    x = requests.post(url+"/posts/comments/like",
                      headers={"Authorization": "Bearer " + john_token},
                      json={"email": "john@user.com", "comment_id": "5"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Same person tries to like same post again
    x = requests.post(url+"/posts/comments/like",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "comment_id": "1"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # User tries to like post that does not exist
    x = requests.post(url+"/posts/comments/like",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "comment_id": "1000"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Fake email in json data
    x = requests.post(url+"/posts/comments/like",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "fake@user.com", "comment_id": "1"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Try unliking comment and then liking it again
    x = requests.post(url+"/posts/comments/unlike",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "comment_id": "1"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    x = requests.post(url+"/posts/comments/like",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "comment_id": "1"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)


def test_unlike_comment():
    print("===== UNLIKE COMMENTS TESTS =====\n\n")

    # Normal unlike
    x = requests.post(url+"/posts/comments/unlike",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "comment_id": "1"})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Unlike post user has already unliked
    x = requests.post(url+"/posts/comments/unlike",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "comment_id": "1"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # False email
    x = requests.post(url+"/posts/comments/unlike",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "fake@user.com", "comment_id": "1"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Bad id
    x = requests.post(url+"/posts/comments/unlike",
                      headers={"Authorization": "Bearer " + jess_token},
                      json={"email": "jess@user.com", "comment_id": "1000"})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)


def test_delete_comment():
    print("===== DELETE COMMENT TESTS =====\n\n")

    # Invalid email
    x = requests.delete(url+"/posts/comments/delete/fake@user.com/3",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Another user tries to delete someone else's comment
    x = requests.delete(url+"/posts/comments/delete/jess@user.com/3",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Correct delete request
    x = requests.delete(url+"/posts/comments/delete/john@user.com/3",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Delete comment with like. This should also delete the like from the database
    x = requests.delete(url+"/posts/comments/delete/john@user.com/5",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)


def test_is_post_liked():
    print("===== CHECK IF POST IS LIKED =====\n\n")

    # Invalid email
    x = requests.get(url+"/posts/ispostliked/fake@user.com/3",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # correct request
    x = requests.get(url+"/posts/ispostliked/john@user.com/3",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Invalid post_id
    x = requests.get(url+"/posts/ispostliked/john@user.com/999",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # Invalid input
    x = requests.get(url+"/posts/ispostliked/john@user.com/",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 404, print("Response code:", x.status_code)


def test_is_comment_liked():
    print("===== CHECK IF COMMENT IS LIKED =====\n\n")
    
        # Invalid email
    x = requests.get(url+"/posts/iscommentliked/fake@user.com/3",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)

    # correct request
    x = requests.get(url+"/posts/iscommentliked/john@user.com/3",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)


def test_is_user_owner_of_post():
    print("===== CHECK IF USER IS OWNER OF POST =====\n\n")
    
    # Normal request
    x = requests.get(url+"/posts/isuserowner/john@user.com/1",
                      headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    correct_response = json.loads("""{"status": "success", "message": "true"}""")
    assert x.json() == correct_response, print("Response text:", x.text)

    # Normal request
    x = requests.get(url+"/posts/isuserowner/jess@user.com/2",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    correct_response = json.loads("""{"status": "success", "message": "true"}""")
    assert x.json() == correct_response, print("Response text:", x.text)

    # User is not owner of post
    x = requests.get(url+"/posts/isuserowner/john@user.com/2",
                      headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    correct_response = json.loads("""{"status": "success", "message": "false"}""")
    assert x.json() == correct_response, print("Response text:", x.text)

    # Invalid email
    x = requests.get(url+"/posts/isuserowner/fake@user.com/2",
                      headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)


def test_get_users_from_search():
    print("===== GET USERS FROM SEARCH =====\n\n")
    
    # Normal request
    x = requests.get(url+"/users/search/john",
                      headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Normal request
    x = requests.get(url+"/users/search/j",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Normal request
    x = requests.get(url+"/users/search/a",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Bad token
    x = requests.get(url+"/users/search/john",
                      headers={"Authorization": "Bearer asdf"})
    print(x.text)
    assert x.status_code == 422, print("Response code:", x.status_code)


def test_is_user_owner_of_comment():
    print("===== CHECK IF USER IS OWNER OF COMMENT =====\n\n")

    # Normal request
    x = requests.get(url+"/posts/comments/isuserowner/jess@user.com/1",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    correct_response = json.loads("""{"status": "success", "message": "true"}""")
    assert x.json() == correct_response, print("Response text:", x.text)

    # Normal request
    x = requests.get(url+"/posts/comments/isuserowner/john@user.com/2",
                      headers={"Authorization": "Bearer " + john_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    correct_response = json.loads("""{"status": "success", "message": "true"}""")
    assert x.json() == correct_response, print("Response text:", x.text)

    # User is not owner of comment
    x = requests.get(url+"/posts/comments/isuserowner/jess@user.com/2",
                    headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)
    correct_response = json.loads("""{"status": "success", "message": "false"}""")
    assert x.json() == correct_response, print("Response text:", x.text)

    # Invalid email
    x = requests.get(url+"/posts/comments/isuserowner/fake@user.com/2",
                      headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)


def test_get_comments_on_post():
    print("===== GET COMMENTS ON POST TESTS =====\n\n")

    # Normal request
    x = requests.get(url+"/posts/comments/get/2",
                     headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 200, print("Response code:", x.status_code)

    # Invalid post_id
    x = requests.get(url+"/posts/comments/get/999",
                     headers={"Authorization": "Bearer " + jess_token})
    print(x.text)
    assert x.status_code == 400, print("Response code:", x.status_code)


if __name__ == "__main__":
    
    # Create users and login
    test_create_user()
    test_user_login()
    
    # Create posts and comments
    test_create_post()
    test_create_comment()
    
    # Get request tests
    test_get_user_data()
    test_get_user_posts()
    test_get_post()
    test_get_feed_post()

    # Follow/unfollow users
    test_user_follow()
    test_user_unfollow()
    test_get_following_feed()
    test_get_is_following()
    test_is_user_owner_of_comment()
    test_is_user_owner_of_post()
    test_get_comments_on_post()
    test_get_users_from_search()

    # Like/unlike posts and comments
    test_like_post()
    test_unlike_post()
    
    test_is_post_liked()    # check if post is liked, put it in the middle just in case the other function delete likes
    
    test_like_comment()
    test_unlike_comment()

    test_is_comment_liked()    # check if comment is liked, put it in the middle just in case the other function delete likes

    test_get_leaderboard()
    test_get_user_comments()    # Get user comments after creating comments
    
    # Delete the posts and comments
    test_delete_post()
    test_delete_comment()

    test_user_logout()

    print("===== PASSED ALL TESTS =====")