from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt
from flask_bcrypt import generate_password_hash, Bcrypt
from functools import wraps
from datetime import timedelta
from dotenv import load_dotenv
from validate_email import validate_email
from werkzeug.utils import secure_filename
from sqlalchemy.sql.expression import func
import os, base64, random, json

app = Flask(__name__)

if 'AZURE_POSTGRESQL_CONNECTIONSTRING' in os.environ:  # running on Azure: use postgresql
    conn = os.environ["AZURE_POSTGRESQL_CONNECTIONSTRING"]
    values = dict(x.split("=") for x in conn.split(" "))
    user = values["user"]
    host = values["host"]
    database = values["dbname"]
    password = values["password"]
    db_url = f"postgresql+psycopg2://{user}:{password}@{host}/{database}"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url

else:   # when running locally: use sqlite
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///./our.db"

load_dotenv()
app.config["JWT_SECRET_KEY"] = "jGagFq3IK5sMr8r"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
db = SQLAlchemy(app)


class Users(db.Model):
    """ This class represents a user in the app.
    parameters:
        username - The username of the user. Does not need to be unique.
        email - The email of the user. Must be unique. Primary key.
        password - The password of the user. Salted and hashed.
        points - The number of points the user has. Points is calculated as the total number of likes
                 A user has across all their posts and comments.
    """
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, primary_key=True, unique=True)
    password = db.Column(db.String, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    followers = db.Column(db.Integer, nullable=False, default=0)


    def __init__(self, username, email, password, points):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password).decode("utf-8")    # Salt and hash the password
        self.points = points
        self.followers = 0

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "points": self.points,
        }


class Follower(db.Model):
    """ This class represent a follower of a user.
    parameters:
        id: Primary key
        following_email: The user who is being followed
        follower_email: The user who is following someone else
        """
    id = db.Column(db.Integer, primary_key=True)
    following_email = db.Column(db.String, db.ForeignKey("users.email"), nullable=False)
    follower_email = db.Column(db.String, db.ForeignKey("users.email"), nullable=False)


class Posts(db.Model):
    """ This class represents a single post in the app.
    parameters:
        post_id: The id of the post. Primary key.
        user_email: The email address of the user who posted the post.
        caption: A text field which should have a question or similar.
        likes: The number of likes the post has.
        img: The image of the post stored as a BLOB.
        """
    post_id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String, db.ForeignKey("users.email"), nullable=False)
    caption = db.Column(db.String, nullable=False)
    likes = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String, nullable=False)
    img = db.Column(db.Text, nullable=False)

    def to_dict(self):
        base64_img = base64.b64encode(self.img)
        return {
            "post_id": self.post_id,
            "user_email": self.user_email,
            "caption": self.caption,
            "likes": self.likes,
            "address": self.address,
            "img": base64_img.decode("utf-8"),
        }


class UserLikesPost(db.Model):
    """ This table stores which users have liked what posts.
    parameters:
        liked - boolean (-1 or 1) if a user has liked/unliked a post
        user_email - email of the user who liked/unliked the post
        post_id - id of the post that was liked/unliked
    """
    id = db.Column(db.Integer, primary_key=True)
    liked = db.Column(db.Integer, nullable=False)
    user_email = db.Column(db.String, db.ForeignKey("users.email"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.post_id"), nullable=False)


class Comments(db.Model):
    """ This class represents a single comment in the app.
    parameters:
        comment_id: The id of the comment. Primary key.
        post_id: The id of the post that the comment belongs to.
        user_email: The email address of the user who posted the comment.
        comment_string: The text of the comment.
        likes: The number of likes the comment has.    
    """
    comment_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.post_id"), nullable=False)
    user_email = db.Column(db.String, db.ForeignKey("users.email"), nullable=False)
    comment_string = db.Column(db.String, nullable=False)
    likes = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        user = Users.query.filter_by(email=self.user_email).first()
        return {
            "comment_id": self.comment_id,
            "post_id": self.post_id,
            "user_email": self.user_email,
            "username": user.username,
            "comment_string": self.comment_string,
            "likes": self.likes,
        }


class UserLikesComment(db.Model):
    """ This table store which users have liked what comments.
    parameters:
        liked - boolean (-1 or 1) if a user has liked/unliked a post
        user_email - email of the user who liked/unliked the post
        comment_id - id of the comment that was liked/unliked
    """
    id = db.Column(db.Integer, primary_key=True)
    liked = db.Column(db.Integer, nullable=False)
    user_email = db.Column(db.String, db.ForeignKey("users.email"), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.comment_id"), nullable=False)


class JWT_blocklist(db.Model):
    """ This class handles the expired tokens """
    block_id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String)


def is_valid_input(lst):
    """ Checks if the given list contains only true value (no NoneType etc) """
    return all(lst)


@app.route("/")
def main_page():
    """ Main page """
    return jsonify({"status": "success", "message": "Main page"}), 200


@app.errorhandler(500)
def internal_error():
    """ Catch all 500 errors """
    return jsonify({"status": "fail", "message": "Internal error"}), 500


@app.route("/users/create", methods=["POST"])
def create_user():
    """ Creates a user.
    Takes following JSON format: 
    {
        "username": <username>,
        "email": <email>,
        "password": <password>
    }
    Returns no data.
    """
    if request.is_json:
        payload = request.get_json()
        username = payload["username"]
        email = payload["email"] 
        password = payload["password"]

        if not is_valid_input([username, email, password]):
            return jsonify({"status": "fail", "message": "Invalid input"}), 400
        
        # Check if email is valid
        if not validate_email(email):
            return jsonify({"status": "fail", "message": "E-mail is invalid"}), 400

        # Check if email is taken
        user = Users.query.filter_by(email=email).first()
        if user is not None:
            return jsonify({"status": "fail", "message": "E-mail already taken"}), 400
        
        # Check if username is taken
        user = Users.query.filter_by(username=username).first()
        if user is not None:
            return jsonify({"status": "fail", "message": "Username already taken"}), 400
        
        # After checking both email and username, create new user
        user = Users(username, email, password, 0)
        db.session.add(user)
        db.session.commit()
        return jsonify({"status": "success", "message": "Successfully created user"})

    return jsonify({"status": "fail", "message": "No JSON data attached"}), 400


@app.route("/users/login", methods=["POST"])
def login():
    """ Returns a generated token after checking email and password 
    Takes following JSON parameters:
    {
        "email": <email>,
        "password": <password>
    }
    Returns the following JSON data if successful:
    {
        "status": "success",
        "message": "Successfully got token.",
        "token": <token>
    }
    """

    if request.is_json:
        payload = request.get_json()
        email = payload["email"]
        password = payload["password"]

        if not is_valid_input([email, password]):
            return jsonify({"status": "fail", "message": "Invalid input"}), 400

        # Check if given email is valid
        if not validate_email(email):
            return jsonify({"status": "fail", "message": "No such user or wrong password"}), 400

        # Check if given email has created a user
        user = Users.query.filter_by(email=email).first()
        if user is None:
            return jsonify({"status": "fail", "message": "No such user or wrong password"}), 400

        # Check if the passwords correlate
        if not bcrypt.check_password_hash(user.password, password):
            return jsonify({"status": "fail", "message": "No such user or wrong password"}), 400
        
        access_token = create_access_token(identity=user.email)
        return jsonify({"status": "success", "message" : "Successfully got token.", "token": access_token})
    
    return jsonify({"status": "fail", "message": "No JSON data attached"}), 400


@app.route("/users/logout", methods=["POST"])
@jwt_required()
def logout():
    """ Marks a users token as expired 
    User needs to be logged in and send token in header """
    jti = get_jwt()["jti"]
    blocked_token = JWT_blocklist(token=jti)
    db.session.add(blocked_token)
    db.session.commit()
    return jsonify({"status": "success", "message": "Successfully logged out"})


@app.route("/users/get/data/<email>", methods=["GET"])
@jwt_required()
def get_user_about(email):
    """ This function returns a given users username, points and how many
    posts this user has uploaded.
    Takes the following route arguments:
        * email - the email of the user of which we want to get the about info
    Returns the following JSON data if successful:
    {
        "status": "success",
        "message": "Successfully got data",
        "user": [
            {
                "email": <str:email>,
                "username": <str:username>,
                "points": <int:points>,
                "posts_amount": <int:posts>
                "followers": <int:followers>
            }
        ]
    }
    """

    if not is_valid_input([email]):
        return jsonify({"status": "fail", "message": "Invalid input"}), 400
    
    # Query for email
    user = Users.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"status": "fail", "message": "Such a user does not exist"}), 400
    
    # Calculate how many posts this user has made
    posts = Posts.query.filter_by(user_email=email).all()
    posts = len(posts)

    user_dict = {
        "email": user.email,
        "username": user.username,
        "points": user.points,
        "posts_amount": posts,
        "followers": user.followers
    }
    
    # Return the data
    return jsonify({"status": "success",
                    "message": "Successfully got data",
                    "user": user_dict}), 200


@app.route("/users/get/posts/<email>", methods=["GET"])
@jwt_required()
def get_user_posts(email):
    """ This function returns a list of the posts a
    user has uploaded.
    Takes the following route arguments:
        * email - the email of the user of which we want to get the posts
    Returns the following JSON data if successful:
    {
        "status": "success",
        "message": "Successfully got posts",
        "posts": [
            {
                "post_id": <int:post_id>,
                "user_email": <str:user_email>,
                "caption": <str:caption>,
                "likes": <int:likes>,
                "address": <str:address>,
                "img": <base64 encoded picture>
            },
            {
                ...
            }
        ]
    }
    """

    if not is_valid_input([email]):
        return jsonify({"status": "fail", "message": "Invalid input"}), 400
    
    # Query for email
    user = Users.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"status": "fail", "message": "Such a user does not exist"}), 400
    
    # Query for posts
    posts = Posts.query.filter_by(user_email=email).all()
    if posts is None:
        # If we get here, the user has not uploaded any posts. Return an empty list
        posts = []
    else:
        # If we get here, the user has uploaded at least one post
        # Add all posts in a list
        posts = [post.to_dict() for post in posts]
    
    # Return the data
    return jsonify({"status": "success",
                    "message": "Successfully got posts",
                    "posts": posts}), 200


@app.route("/users/search/<query>", methods=["GET"])
@jwt_required()
def get_users_from_search(query):

    if not is_valid_input([query]):
        return jsonify({"status": "fail", "message": "Invalid input"}), 400
    
    # Query for users
    users = Users.query.filter(Users.username.like(f"%{query}%")).all()
    if users is None:
        return jsonify({"status": "fail", "message": "No such user"}), 400
    
    # Add all users in a list
    users = [user.to_dict() for user in users]
    
    # Return the data
    return jsonify({"status": "success",
                    "message": "Successfully got users",
                    "users": users}), 200


@app.route("/users/get/comments/<email>", methods=["GET"])
@jwt_required()
def get_user_comments(email):
    """ This function returns a list of the comments a
    user has uploaded. 
    Takes the following route arguments:
        * email - the email of the user who owns the comments
    Returns the following JSON data if successful:
    {
        "status": "success",
        "message": "Successfully got comments",
        "comments": [
            {
            "comment_id": <int:comment_id>,
            "post_id": <int:post_id>,
            "user_email": <str:user_email>,
            "username": <str:username>,
            "comment_string": <str:comment_string>,
            "likes": <int:likes>,
            }
        ]
    }
    """
        
    if not is_valid_input([email]):
        return jsonify({"status": "fail", "message": "Invalid input"}), 400
    
    # Query for email
    user = Users.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"status": "fail", "message": "Such a user does not exist"}), 400
    
    # Query for comments
    comments = Comments.query.filter_by(user_email=email).all()
    if comments is None:
        # If we get here, the user has not uploaded any comments. Return an empty list
        comments = []
    else:
        # If we get here, the user has uploaded at least one comment
        # Add all comments in a list
        comments = [comment.to_dict() for comment in comments]
    
    # Return the data
    return jsonify({"status": "success",
                    "message": "Successfully got comments",
                    "comments": comments}), 200
    

@app.route("/users/get/leaderboard", methods=["GET"])
@jwt_required()
def get_leaderboard():
    """ This function returns the top 10 users usernames with the
    most amount of points to display on the leaderboard.
    The returned list is SORTED based on amount of points.
    Does not take any input.
    Returns the following JSON data if successful:
    {
        "status": "success",
        "message": "Successfully got data",
        "users": [
            {
                "email": <str:email1>,
                "username": <str:username1>,
                "points": <int:points1>
            },
            {
                "email": <str:email2>,
                "username": <str:username2>,
                "points": <int:points2>
            },
            ...
        ]
    }
    """

    # Query for all users
    users = Users.query.all()
    if users is None:
        return jsonify({"status": "fail", "message": "No users in database"}), 400
    
    # Add all users in a list
    users = [user.to_dict() for user in users]
    
    # Sort the list by points
    users = sorted(users, key=lambda x: x["points"], reverse=True)
    
    # Return the data
    return jsonify({"status": "success",
                    "message": "Successfully got data",
                    "users": users[:10]}), 200


@app.route("/feed/get", methods=["GET"])
@jwt_required()
def get_feed_post():
    """ This function returns a random post in the database
    to display on the main feed of the app
    Does not take any input.
    Returns the following JSON data if successful:
    {
        "status": "success",
        "message": "Successfully got post",
        "post": [
            {
                "username": <str:username>,
                "user_email": <str:email>,
                "address": <str:address>,
                "post_id": <int:post_id>,
                "amount_of_comments": <int:amount_of_comments>,
                "caption": <str:caption>,
                "likes": <int:likes>,
                "img": <base64 encoded picture>
            }
        ]
    }
    """
    
    # Get a random post
    random_post = Posts.query.order_by(func.random()).first()
    if random_post is None:
        return jsonify({"status": "fail", "message": "No posts in database"}), 404
    
    # Get the username of the user who posted the post
    user_email = random_post.user_email
    user = Users.query.filter_by(email=user_email).first()
    username = user.username

    # Get the amount of comments on the post
    comments = Comments.query.filter_by(post_id=random_post.post_id).all()
    amount_of_comments = len(comments)
    
    post_dict = random_post.to_dict();

    post = {
        "username": username,
        "user_email": post_dict["user_email"],
        "address": post_dict["address"],
        "post_id": post_dict["post_id"],
        "caption": post_dict["caption"],
        "amount_of_comments": amount_of_comments,
        "likes": post_dict["likes"],
        "img": post_dict["img"]

    }
    
    # Return the data
    return jsonify({"status": "success",
                    "message": "Successfully got post",
                    "post": post}), 200



@app.route("/posts/get/<post_id>", methods=["GET"])
@jwt_required()
def get_post(post_id):
    """ This function will get a post given the post_id
    Takes the following route arguments:
        * post_id - the id of the post we want to get
    Returns the following JSON data if successful:
    {
        "status": "success",
        "message": "Successfully got post",
        "post": {
            "username": <str:username>,
            "user_email": <str:user_email>,
            "address": <str:address>,
            "post_id": <int:post_id>,
            "amount_of_comments": <int:ammount_of_comments>,
            "caption": <str:caption>,
            "likes": <int:likes>,
            "img": <base64 encoded picture>
        }
    }
    """

    if not is_valid_input([post_id]):
        return jsonify({"status": "fail", "message": "Invalid input"}), 400
    
    # Query for post
    post = Posts.query.filter_by(post_id=post_id).first()
    if post is None:
        return jsonify({"status": "fail", "message": "Such a post does not exist"}), 400
    
    # Get the username of the user who posted the post
    user_email = post.user_email
    user = Users.query.filter_by(email=user_email).first()
    username = user.username

    post_dict = post.to_dict()

    # Calculate the amount of comments on the post
    comments = Comments.query.filter_by(post_id=post_id).all()
    amount_of_comments = len(comments)
        
    # Return the data
    return jsonify({"status": "success",
                    "message": "Successfully got post",
                    "post": {
                        "username": username,
                        "user_email": user_email,
                        "address": post_dict["address"],
                        "post_id": post_dict["post_id"],
                        "amount_of_comments": amount_of_comments,
                        "caption": post_dict["caption"],
                        "likes": post_dict["likes"],
                        "img": post_dict["img"]
                    }}), 200


@app.route("/posts/create", methods=["POST"])
@jwt_required()
def create_post():
    """ Create a new post.
    Takes the following JSON parameters: 
    {
        "email": <email>,
        "caption": <caption>
        "address": <address>
        "picture": <base64 encoded picture>
    }
    Returns no data
    """

    if request.is_json:
        payload = request.get_json()
        email = payload["email"]
        caption = payload["caption"]
        base64_picture = payload["picture"]
        address = payload["address"]

        if not is_valid_input([email, caption, base64_picture]):
            return jsonify({"status": "fail", "message": "Invalid input"}), 400

        # Check if email in db
        user = Users.query.filter_by(email=email).first()
        if user is None:
            return jsonify({"status": "fail", "message": "Such a user does not exist"}), 400

        # Decode the base64 picture into binary data
        try:
            image_data = base64.b64decode(base64_picture)
        except (ValueError, TypeError) as e:
            return jsonify({"status": "fail", "message": "Invalid base64 image data"}), 400

        # Add the post to the database
        post = Posts(user_email=email, caption=caption, address=address, likes=0, img=image_data)
        db.session.add(post)
        db.session.commit()
        return jsonify({"status": "success", "message": "Successfully created post"}), 200
    
    return jsonify({"status": "fail", "message": "No JSON data attached"}), 400


@app.route("/posts/like", methods=["POST"])
@jwt_required()
def like_post():
    """ Like a post.
    Takes the following JSON parameters:
    {
        "email": <email>,
        "post_id": <post_id>
    }
    Returns no data.
    """
    
    if request.is_json:
        payload = request.get_json()
        email = payload["email"]
        post_id = payload["post_id"]

        # Check if email and post_id are valid and in database

        if not is_valid_input([email, post_id]):
            return jsonify({"status": "fail", "message": "Invalid input"}), 400
        
        user = Users.query.filter_by(email=email).first()
        post = Posts.query.filter_by(post_id=post_id).first()
        if (user is None) or (post is None):
            return jsonify({"status": "fail", "message": "Such a user or post does not exist"}), 400

        # Check if user has already disliked post
        user_likes_post = UserLikesPost.query.filter_by(user_email=email, post_id=post_id).first()
        if user_likes_post is not None:
            # If user already has liked post, send fail message
            if user_likes_post.liked == 1:
                return jsonify({"status": "fail", "message": "User has already liked this post"}), 400
            
            # If a user has disliked post before, mark as liked
            elif user_likes_post.liked == -1:
                user_likes_post.liked = 1 
                post.likes += 1

                # Add a point to the post owner
                post_owner = Users.query.filter_by(email=post.user_email).first()
                post_owner.points += 1

                db.session.commit()
                return jsonify({"status": "success", "message": "User successfully liked post"}), 200
        
        # If we get here, then user has not previously liked post. Create new UserLikesPost instance
        # and add 1 to post.likes
        user_likes_post = UserLikesPost(user_email=email, post_id=post_id, liked=1)
        post.likes += 1

        # Add a point to the post owner
        post_owner = Users.query.filter_by(email=post.user_email).first()
        post_owner.points += 1

        db.session.add(user_likes_post)
        db.session.commit()
        
        return jsonify({"status": "success", "message": "Successfully liked post"}), 200
    
    return jsonify({"status": "fail", "message": "No JSON data attached"}), 400


@app.route("/posts/ispostliked/<email>/<post_id>", methods=["GET"])
@jwt_required()
def is_post_liked(email, post_id):
    """ get a post like status.
    Take the following route arguments:
        * email - the email of the user who we want to check has liked or not
        * post_id - the post of which we want to check the user has liked or not
    Returns no data.
    """

    # Check if email and post_id are valid and in database
    if not is_valid_input([email, post_id]):
        return jsonify({"status": "fail", "message": "Invalid input"}), 400
    
    user = Users.query.filter_by(email=email).first()
    post = Posts.query.filter_by(post_id=post_id).first()
    if (user is None) or (post is None):
        return jsonify({"status": "fail", "message": "Such a user or post does not exist"}), 400
    
    # Check if user has liked post already
    user_likes_post = UserLikesPost.query.filter_by(user_email=email, post_id=post_id).first()

    if user_likes_post is not None:
        # Now we know that the user has interacted with this post's likes before
        if user_likes_post.liked == 1:
            return jsonify({"status": "success", "message": "User has already liked this post"}), 200
        elif user_likes_post.liked == -1:        
            return jsonify({"status": "success", "message": "User hasn't liked this post"}), 200

    # If we get here, it means the user has not interacted with this post, and therefore not liked it    
    return jsonify({"status": "sucess", "message": "User hasn't liked this post"}), 200
        

@app.route("/posts/unlike", methods=["POST"])
@jwt_required()
def unlike_post():
    """ Unlike a post.
    Takes the following JSON parameters:
    {
        "email": <email>,
        "post_id": <post_id>
    }
    Returns no data.
    """
    
    if request.is_json:
        payload = request.get_json()
        email = payload["email"]
        post_id = payload["post_id"]

        # Check if email and post_id are valid and in database
        if not is_valid_input([email, post_id]):
            return jsonify({"status": "fail", "message": "Invalid input"}), 400
        
        user = Users.query.filter_by(email=email).first()
        post = Posts.query.filter_by(post_id=post_id).first()
        if (user is None) or (post is None):
            return jsonify({"status": "fail", "message": "Such a user or post does not exist"}), 400
        
        # Check if user has liked post already
        user_likes_post = UserLikesPost.query.filter_by(user_email=email, post_id=post_id).first()
        if user_likes_post is not None:
            # If user already has disliked post, send fail message
            if user_likes_post.liked == -1:
                return jsonify({"status": "fail", "message": "User has already unliked this post"}), 400
            
            # If a user has liked post before, mark as disliked
            elif user_likes_post.liked == 1:
                user_likes_post.liked = -1
                post.likes -= 1

                # Subtract a point from the post owner
                post_owner = Users.query.filter_by(email=post.user_email).first()
                post_owner.points -= 1
                db.session.commit()
                return jsonify({"status": "success", "message": "User successfully disliked post"}), 200
            
        # If we get here, then user has not liked post before.
        # Send fail message since post must be liked to be unliked
        return jsonify({"status": "fail", "message": "User has not liked this post"}), 400

    return jsonify({"status": "fail", "message": "No JSON data attached"}), 400


@app.route("/posts/delete/<email>/<post_id>", methods=["DELETE"])
@jwt_required()
def delete_post(email, post_id):
    """ Delete a post.
    Takes the following route arguments:
        * email - the email of the user who requested the deletion
        * post_id - the post id of which we want to delete
    Returns no data.
    """

    # Check if email and post_id are valid
    if not is_valid_input([email, post_id]):
        return jsonify({"status": "fail", "message": "Invalid input"}), 400
    
    user = Users.query.filter_by(email=email).first()
    post = Posts.query.filter_by(post_id=post_id).first()
    if (user is None) or (post is None):
        return jsonify({"status": "fail", "message": "Such a user or post does not exist"}), 400
    
    # Check if user is the owner of the post
    if email != post.user_email:
        return jsonify({"status": "fail", "message": "User is not the owner of this post"}), 400
    
    # Subtract a point from the post owner
    post_owner = Users.query.filter_by(email=post.user_email).first()
    post_owner.points -= post.likes

    # Delete likes on comments on this post
    comments = Comments.query.filter_by(post_id=post_id).all()
    for comment in comments:
        user_likes_comments = UserLikesComment.query.filter_by(comment_id=comment.comment_id).all()
        for user_likes_comment in user_likes_comments:
            db.session.delete(user_likes_comment)

    # Delete related comments to this post
    comments = Comments.query.filter_by(post_id=post_id).all()
    for comment in comments:
        db.session.delete(comment)

    # Delete related likes to this post
    user_likes_posts = UserLikesPost.query.filter_by(post_id=post_id).all()
    for user_likes_post in user_likes_posts:
        db.session.delete(user_likes_post)
    
    # Delete the post from the database
    db.session.delete(post)
    db.session.commit()

    return jsonify({"status": "success", "message": "Successfully deleted post"}), 200


@app.route("/posts/comments/add", methods=["POST"])
@jwt_required()
def post_comment():
    """ Create a new comment on a post. 
    Takes the following JSON parameters:
    {
        "email": <email>,
        "post_id": <post_id>,
        "comment": <comment>
    }
    Returns Tthe following JSON data if successful:
    {
        "status": "success",
        "message": "Successfully created comment"
        "comment": {
            "comment_id": <comment_id>,
            "post_id": <post_id>,
            "user_email": <user_email>,
            "comment_string": <comment_string>,
            "likes": <likes>
        }
    }
    """

    if request.is_json:
        payload = request.get_json()
        email = payload["email"]
        post_id = payload["post_id"]
        comment = payload["comment"]

        if not is_valid_input([email, post_id, comment]):
            return jsonify({"status": "fail", "message": "Invalid input"}), 400
        
        # Check if email and post id are in database
        user = Users.query.filter_by(email=email).first()
        post = Posts.query.filter_by(post_id=post_id).first()
        if (user is None) or (post is None):
            return jsonify({"status": "fail", "message": "Such a user or post does not exist"}), 400
        
        # Add the comment to the database
        comment = Comments(post_id=post_id, user_email=email, comment_string=comment, likes=0)
        db.session.add(comment)
        db.session.commit()

        comment_dict = comment.to_dict()

        return jsonify({"status": "success",
                        "message": "Successfully created comment",
                        "comment": comment_dict}), 200
    
    return jsonify({"status": "fail", "message": "No JSON data attached"}), 400


@app.route("/posts/comments/like", methods=["POST"])
@jwt_required()
def like_comment():
    """ Like a comment.
    Takes the following JSON parameters: 
    {
        "email": <email>,
        "comment_id": <comment_id>
    }
    Returns no data.
    """
    
    if request.is_json:
        payload = request.get_json()
        email = payload["email"]
        comment_id = payload["comment_id"]

        # Check if email and comment_id are valid
        if not is_valid_input([email, comment_id]):
            return jsonify({"status": "fail", "message": "Invalid input"}), 400
        
        user = Users.query.filter_by(email=email).first()
        comment = Comments.query.filter_by(comment_id=comment_id).first()
        if (user is None) or (comment is None):
            return jsonify({"status": "fail", "message": "Such a user or comment does not exist"}), 400
        
        # Check if user has already liked comment
        user_likes_comment = UserLikesComment.query.filter_by(user_email=email, comment_id=comment_id).first()
        if user_likes_comment is not None:
            
            # If user has already liked comment, send fail message
            if user_likes_comment.liked == 1:
                return jsonify({"status": "fail", "message": "User has already liked this comment"}), 400
            
            # If user has disliked comment previously, mark as liked
            elif user_likes_comment.liked == -1:
                user_likes_comment.liked = 1 
                comment.likes += 1

                # Add a point to the comment owner
                comment_owner = Users.query.filter_by(email=comment.user_email).first()
                comment_owner.points += 1

                db.session.commit()
                return jsonify({"status": "success", "message": "User successfully liked comment"}), 200
        
        # If we get here, then user has not previously liked post. Create new UserLikesComment instance
        # and add 1 to comment.likes
        user_likes_comment = UserLikesComment(user_email=email, comment_id=comment_id, liked=1)
        comment.likes += 1

        # Add a point to the comment owner
        comment_owner = Users.query.filter_by(email=comment.user_email).first()
        comment_owner.points += 1

        db.session.add(user_likes_comment)
        db.session.commit()
        
        return jsonify({"status": "success", "message": "Successfully liked comment"}), 200
    
    return jsonify({"status": "fail", "message": "No JSON data attached"}), 400
    

@app.route("/posts/iscommentliked/<email>/<comment_id>", methods=["GET"])
@jwt_required()
def is_comment_liked(email, comment_id):
    """ get a post like status.
    Takes the following route arguments:
        * email - the email of the user who we want to check has liked the comment or not
        * comment_id - the comment_id of the comment we want to check has been liked or not
    Returns no data.
    """
        
    # Check if email and comment_id are valid
    if not is_valid_input([email, comment_id]):
        return jsonify({"status": "fail", "message": "Invalid input"}), 400
    
    user = Users.query.filter_by(email=email).first()
    comment = Comments.query.filter_by(comment_id=comment_id).first()
    if (user is None) or (comment is None):
        return jsonify({"status": "fail", "message": "Such a user or comment does not exist"}), 400
    
    # Check if user has liked comment already
    user_likes_comment = UserLikesComment.query.filter_by(user_email=email, comment_id=comment_id).first()
    if user_likes_comment is not None:

        # Now we know the user has interacted with this comment's likes before
        if user_likes_comment.liked == 1:
            return jsonify({"status": "success", "message": "User has already liked this comment"}), 200
        
        elif user_likes_comment.liked == -1:
            return jsonify({"status": "success", "message": "User hasn't liked this comment"}), 200
        
    # If we get here, then user has not previously liked the comment
    return jsonify({"status": "success", "message": "User hasn't liked this comment"}), 200


@app.route("/posts/isuserowner/<email>/<post_id>", methods=["GET"])
@jwt_required()
def is_user_owner_of_post(email, post_id):
    """ This function will return "true" if the given user
    is the owner of the post with the given post_id.
    Takes the following route arguments:
        * email - the email of the user who we want to check
        * post_id - the id of the post
    Returns the following JSON data if successful:
        {
            "status": "success",
            "message": "true" or "false"
        }
    """

    if not is_valid_input([email, post_id]):
        return jsonify({"status": "fail", "message": "Invalid input"}), 400
    
    user = Users.query.filter_by(email=email).first()
    post = Posts.query.filter_by(post_id=post_id).first()
    if (user is None) or (post is None):
        return jsonify({"status": "fail", "message": "Such a user or post does not exist"}), 400
    
    # Check if user is the owner of the post
    if user.email == post.user_email:
        return jsonify({"status": "success", "message": "true"}), 200
    
    return jsonify({"status": "success", "message": "false"}), 200


@app.route("/posts/comments/isuserowner/<email>/<comment_id>", methods=["GET"])
@jwt_required()
def is_user_owner_of_comment(email, comment_id):
    """ This function will return "true" if the user email
    is the owner of the comment with the given comment_id.
    Takes the following route arguments:
        * email - the email of the user who we want to check
        * comment_id - the id of the comment
    Returns the following JSON data if successful:
        {
            "status": "success",
            "message": "true" or "false"
        }
    """

    if not is_valid_input([email, comment_id]):
        return jsonify({"status": "fail", "message": "Invalid input"}), 400
    
    user = Users.query.filter_by(email=email).first()
    comment = Comments.query.filter_by(comment_id=comment_id).first()
    if (user is None) or (comment is None):
        return jsonify({"status": "fail", "message": "Such a user or comment does not exist"}), 400

    # Check if user is the owner of the comment
    if user.email == comment.user_email:
        return jsonify({"status": "success", "message": "true"}), 200
    
    return jsonify({"status": "success", "message": "false"}), 200


@app.route("/posts/comments/unlike", methods=["POST"])
@jwt_required()
def unlike_comment():
    """ Unlike a comment which the user has already liked.
    Takes the following JSON data:
    {
        "email": <email>,
        "comment_id": <comment_id>
    }
    Returns no data.
    """
    
    if request.is_json:
        payload = request.get_json()
        email = payload["email"]
        comment_id = payload["comment_id"]

        # Check if email and comment_id are valid
        if not is_valid_input([email, comment_id]):
            return jsonify({"status": "fail", "message": "Invalid input"}), 400
        
        user = Users.query.filter_by(email=email).first()
        comment = Comments.query.filter_by(comment_id=comment_id).first()
        if (user is None) or (comment is None):
            return jsonify({"status": "fail", "message": "Such a user or comment does not exist"}), 400
        
        # Check if user has liked comment already
        user_likes_comment = UserLikesComment.query.filter_by(user_email=email, comment_id=comment_id).first()
        if user_likes_comment is not None:

            # If a user already has disliked post, send fail message
            if user_likes_comment.liked == -1:
                return jsonify({"status": "fail", "message": "User has already unliked this comment"}), 400
            
            # If a user has liked post before, mark as disliked
            elif user_likes_comment.liked == 1:
                user_likes_comment.liked = -1
                comment.likes -= 1

                # Subtract a point from the comment owner
                comment_owner = Users.query.filter_by(email=comment.user_email).first()
                comment_owner.points -= 1

                db.session.commit()
                return jsonify({"status": "success", "message": "User successfully disliked comment"}), 200
            
        # If we get here, then user has not liked post before.
        # Send fail message since post must be liked to be unliked
        return jsonify({"status": "fail", "message": "User has not liked this comment"}), 400

    return jsonify({"status": "fail", "message": "No JSON data attached"}), 400


@app.route("/posts/comments/get/<post_id>", methods=["GET"])
@jwt_required()
def get_comments_on_post(post_id):
    """ Get all comments on a post.
    Takes the following route arguments:
        * post_id - the id of the post
    Returns the following JSON data if successful:
        {
            "status": "success",
            "message": "Successfully got comments on post",
            "comments": [
                {
                    "comment_id": <comment_id>,
                    "user_email": <user_email>,
                    "comment_text": <comment_text>,
                    "likes": <likes>,
                    "dislikes": <dislikes>,
                    "created_at": <created_at>
                },
               ...
            ]
        }
    """

    post = Posts.query.filter_by(post_id=post_id).first()
    if post is None:
        return jsonify({"status": "fail", "message": "Such a post does not exist"}), 400
    
    comments = Comments.query.filter_by(post_id=post_id).all()
    if comments is None:
        return jsonify({"status": "fail", "message": "There are no comments on this post"}), 400
    
    comments_list = [comment.to_dict() for comment in comments]

    return jsonify({"status": "success",
                    "message": "Successfully got comments on post",
                    "comments": comments_list}), 200
    

@app.route("/posts/comments/delete/<email>/<comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(email, comment_id):
    """ Delete a comment.
    Takes the following route parameters:
        * email - the email of the user who requested the deletion
        * comment_id - the comment id of the comment we want to delete
    Returns no data.
    """
        
    # Check if email and comment_id are valid
    if not is_valid_input([email, comment_id]):
        return jsonify({"status": "fail", "message": "Invalid input"}), 400
    
    user = Users.query.filter_by(email=email).first()
    comment = Comments.query.filter_by(comment_id=comment_id).first()
    if (user is None) or (comment is None):
        return jsonify({"status": "fail", "message": "Such a user or post does not exist"}), 400
    
    # Check if user is the owner of the post
    if email != comment.user_email:
        return jsonify({"status": "fail", "message": "User is not the owner of this comment"}), 400
    
    # Remove points equivalent to amount of likes
    comment_owner = Users.query.filter_by(email=comment.user_email).first()
    comment_owner.points -= comment.likes

    # Remove related likes on comment  
    user_likes_comments = UserLikesComment.query.filter_by(comment_id=comment_id).all()
    for user_likes_comment in user_likes_comments:
        db.session.delete(user_likes_comment)
    
    # Delete the post from the database
    db.session.delete(comment)
    db.session.commit()

    return jsonify({"status": "success", "message": "Successfully deleted comment"}), 200


@app.route("/users/follow", methods=["POST"])
@jwt_required()
def follow_user():
    """ Follow a user
    Takes the following JSON parameters:
    {
        "following_email": <str:following_email> (the user who is being followed),
        "follower_email": <str:follower_email> (the user who is following)
    }
    Returns no data."""
    
    if request.is_json:
        payload = request.get_json()
        following_email = payload["following_email"]
        follower_email = payload["follower_email"]

        if not is_valid_input([following_email, follower_email]):
            return jsonify({"status": "fail", "message": "Invalid input"}), 400
        
        following_user = Users.query.filter_by(email=following_email).first()
        follower_user = Users.query.filter_by(email=follower_email).first()
        if (follower_user is None) or (following_user is None):
            return jsonify({"status": "fail", "message": "Such a user or follower does not exist"}), 400
        
        if following_user == follower_user:
            return jsonify({"status": "fail", "message": "User can not follow themselves"}), 400
        
        # Check if follower has already followed user
        follower_status = Follower.query.filter_by(follower_email=follower_email, following_email=following_email).first()
        if follower_status is None:
            # If we get here, the user is not following the other person, add them
            follower = Follower(follower_email=follower_email, following_email=following_email)
            # Add one to the followers of followed user
            following_user.followers += 1
            db.session.add(follower)
            db.session.commit()
            return jsonify({"status": "success", "message": "Successfully followed user"}), 200
        
        # If we get here, the user is not following the other person. Send fail message
        return jsonify({"status": "fail", "message": "User is already following this user"}), 400
    
    return jsonify({"status": "fail", "message": "No JSON data attached"}), 400


@app.route("/users/unfollow/<following_email>/<follower_email>", methods=["DELETE"])
@jwt_required()
def unfollow_user(following_email, follower_email):
    """ Unfollow a user
    Takes the following route arguments:
        * following_email - the email of the user who is being followed
        * follower_email - the email of the user who is following the other user
    Returns no data.
    """
    
    if not is_valid_input([following_email, follower_email]):
        return jsonify({"status": "fail", "message": "Invalid input"}), 400
    
    following_user = Users.query.filter_by(email=following_email).first()
    follower_user = Users.query.filter_by(email=follower_email).first()
    if (follower_user is None) or (following_user is None):
        return jsonify({"status": "fail", "message": "Such a user or follower does not exist"}), 400
    
    if following_user == follower_user:
        return jsonify({"status": "fail", "message": "User can not unfollow themselves"}), 400
    
    # Check if follower has already followed user
    follower_status = Follower.query.filter_by(follower_email=follower_email, following_email=following_email).first()
    if follower_status is not None:
        # If we get here, the user is following the other person, remove them
        db.session.delete(follower_status)
        # Subtract one from the followers of followed user
        following_user.followers -= 1
        db.session.commit()
        return jsonify({"status": "success", "message": "Successfully unfollowed user"}), 200
    
    # If we get here, the user is not following the other person. Send fail message
    return jsonify({"status": "fail", "message": "User is not following this user"}), 400
    

@app.route("/users/isfollowing/<follower_email>/<following_email>", methods=["GET"])
@jwt_required()
def get_is_following(follower_email, following_email):
    """ This function check whether a user is following
    another user or not
    Takes the following route arguments:
        * follower_email - the email of the follower
        * following_email - the email of the user being followed
    Returns the following string in the "message" of the JSON response:
        * "true" if the user is following
        * "false" if the user is not following
        """
    
    if not is_valid_input([follower_email, following_email]):
        return jsonify({"status": "fail", "message": "Invalid input"}), 400
    
    follower_user = Users.query.filter_by(email=follower_email).first()
    following_user = Users.query.filter_by(email=following_email).first()
    if (follower_user is None) or (following_user is None):
        return jsonify({"status": "fail", "message": "Such a user or follower does not exist"}), 400
    
    # Check if follower has already followed user
    follower_status = Follower.query.filter_by(follower_email=follower_email, following_email=following_email).first()
    if follower_status is None:
        return jsonify({"status": "success", "message": "false"}), 200
    
    # If we get here, the user is following the other person.
    return jsonify({"status": "success", "message": "true"}), 200


@app.route("/feed/get/following/<email>", methods=["GET"])
@jwt_required()
def get_following_feed(email):
    """ Returns a random post by someone a user is following
    Takes the following route arguments:
        * email - the email of the user who requested the following feed
    Returns the following JSON data if successful:
    {
        "status": "success",
        "message": "Successfully got post",
        "post": {
            "username": <str:username>,
            "user_email": <str:user_email>,
            "address": <str:address>,
            "post_id": <int:post_id>,
            "amount_of_comments": <int:amount_of_comments>,
            "caption": <str:caption>,
            "likes": <int:likes>,
            "img": <base64 encoded picture>
        }
    }
    """
    if not is_valid_input([email]):
        return jsonify({"status": "fail", "message": "Invalid input"}), 400
    
    user = Users.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"status": "fail", "message": "Such a user does not exist"}), 400
    
    # Get the list of users the input user is following
    following_emails_subquery = (
        db.session.query(Follower.following_email)
        .filter(Follower.follower_email == email)
        .subquery()
    )

    # Query for a random post from the users being followed
    random_post = (
        db.session.query(Posts)
        .filter(Posts.user_email.in_(following_emails_subquery))
        .order_by(func.random())
        .first()
    )

    if random_post is None:
        return jsonify({"status": "fail", "message": "No posts found"}), 404

    # Convert the post into the desired format
    user_email = random_post.user_email
    user = Users.query.filter_by(email=user_email).first()
    username = user.username

    comments = Comments.query.filter_by(post_id=random_post.post_id).all()
    amount_of_comments = len(comments)

    post_dict = random_post.to_dict()

    post_data = {
        "username": username,
        "user_email": post_dict["user_email"],
        "address": post_dict["address"],
        "post_id": post_dict["post_id"],
        "caption": post_dict["caption"],
        "amount_of_comments": amount_of_comments,
        "likes": post_dict["likes"],
        "img": post_dict["img"]
    }

    # Return the random post
    return jsonify({
        "status": "success",
        "message": "Successfully got post",
        "post": post_data,
    }), 200

    

@jwt.token_in_blocklist_loader
def check_if_token_expired(jwt_header, jwt_payload:dict):
    jti = jwt_payload["jti"]
    is_token_expired = JWT_blocklist.query.filter_by(token=jti).first()
    return is_token_expired is not None


if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.run(debug=True)
