"""
This is a Flask web application that provides user authentication, profile management, and post interactions.
It uses MongoDB as the database and JWT for user authentication.

Modules:
- Flask: For creating the web application and handling HTTP requests.
- pymongo: For interacting with the MongoDB database.
- jwt: For encoding and decoding JSON Web Tokens.
- hashlib: For hashing passwords.
- werkzeug.utils: For securely handling file uploads.
- os: For accessing environment variables and file paths.
- dotenv: For loading environment variables from a .env file.

Endpoints:
- `/`: Home page that displays user information if logged in.
- `/login`: Login page.
- `/user/<username>`: User profile page.
- `/sign_in`: API endpoint for user login.
- `/sign_up/save`: API endpoint for user registration.
- `/sign_up/check_dup`: API endpoint to check for duplicate usernames.
- `/update_profile`: API endpoint to update user profiles.
- `/posting`: API endpoint to create a new post.
- `/get_posts`: API endpoint to fetch posts.
- `/update_like`: API endpoint to update likes on posts.
- `/about`: About page.
- `/secret`: Secret page accessible only to logged-in users.

"""

# Import necessary modules
# Flask framework for web app and HTTP handling
from flask import Flask, render_template, jsonify, request, redirect, url_for
from pymongo import MongoClient  # MongoDB client for database operations
import jwt  # JSON Web Token for authentication
# For handling time-related operations
from datetime import datetime, timedelta
import hashlib  # For hashing passwords securely
from werkzeug.utils import secure_filename  # For secure file uploads
import os  # For environment variable and file path handling
from os.path import join, dirname  # For constructing file paths
from dotenv import load_dotenv  # For loading environment variables from .env file

# Load environment variables from .env file
dotenv_path = join(dirname(__file__), '.env')  # Path to .env file
load_dotenv(dotenv_path)  # Load environment variables

# Initialize Flask app
app = Flask(__name__)  # Create Flask app instance
# Enable auto-reloading of templates
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Set folder for profile picture uploads
app.config["UPLOAD_FOLDER"] = "./static/profile_pics"

# Load environment variables for database and secret key
MONGODB_CONNECTION_STRING = os.environ.get(
    "MONGODB_CONNECTION_STRING")  # MongoDB connection string
DB_NAME = os.environ.get("DB_NAME")  # Database name
SECRET_KEY = os.environ.get("SECRET_KEY")  # Secret key for JWT

# Initialize MongoDB client and database
client = MongoClient(MONGODB_CONNECTION_STRING)  # Connect to MongoDB
db = client[DB_NAME]  # Access the specified database


#################################
## HTML-related API endpoints  ##
#################################

@app.route("/")
def home():
    """Home page that displays user information if logged in."""
    token_receive = request.cookies.get("mytoken")  # Get token from cookies
    try:
        payload = jwt.decode(token_receive, SECRET_KEY,
                             algorithms=["HS256"])  # Decode JWT
        # Fetch user info from database
        user_info = db.users.find_one({"username": payload["id"]})
        # Render home page with user info
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        # Redirect to login if token expired
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        # Redirect to login if token invalid
        return redirect(url_for("login", msg="There was problem logging you in"))


@app.route("/login")
def login():
    """Login page."""
    msg = request.args.get("msg")  # Get optional message from query params
    # Render login page with message
    return render_template("login.html", msg=msg)


@app.route("/user/<username>")
def user(username):
    """User profile page."""
    token_receive = request.cookies.get("mytoken")  # Get token from cookies
    try:
        payload = jwt.decode(token_receive, SECRET_KEY,
                             algorithms=["HS256"])  # Decode JWT
        # Check if this is the logged-in user's profile
        status = username == payload["id"]

        # Fetch user info from database
        user_info = db.users.find_one({"username": username}, {"_id": False})
        # Render user profile page
        return render_template("user.html", user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        # Redirect to home if token invalid or expired
        return redirect(url_for("home"))


#################################
## Login related API endpoints ##
#################################

@app.route("/sign_in", methods=["POST"])
def sign_in():
    """API endpoint for user login."""
    username_receive = request.form["username_give"]  # Get username from form data
    # Get password from form data
    password_receive = request.form["password_give"]
    pw_hash = hashlib.sha256(password_receive.encode(
        "utf-8")).hexdigest()  # Hash the password
    # Check credentials in database
    result = db.users.find_one(
        {"username": username_receive, "password": pw_hash})
    if result:
        payload = {"id": username_receive, "exp": datetime.utcnow(
        ) + timedelta(seconds=60 * 60 * 24)}  # Create JWT payload
        token = jwt.encode(payload, SECRET_KEY,
                           algorithm="HS256")  # Encode JWT

        # Return success response with token
        return jsonify({"result": "success", "token": token})
    # Let's also handle the case where the id and
    # password combination cannot be found
    else:
        # Return failure response
        return jsonify({"result": "fail", "msg": "We could not find a user with that id/password combination"})


@app.route("/sign_up/save", methods=["POST"])
def sign_up():
    """API endpoint for user registration."""
    username_receive = request.form['username_give']  # Get username from form data
    # Get password from form data
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode(
        'utf-8')).hexdigest()  # Hash the password
    doc = {
        "username": username_receive,  # Store username
        "password": password_hash,  # Store hashed password
        "profile_name": username_receive,  # Default profile name is username
        "profile_pic": "",  # No profile picture initially
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # Default profile picture
        "profile_info": ""  # No profile info initially
    }
    db.users.insert_one(doc)  # Insert user into database
    return jsonify({'result': 'success'})  # Return success response


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    """API endpoint to check for duplicate usernames."""
    username_receive = request.form['username_give']  # Get username from form data
    # Check if username exists in database
    exists = bool(db.users.find_one({"username": username_receive}))
    # Return response with existence status
    return jsonify({'result': 'success', 'exists': exists})


@app.route("/update_profile", methods=["POST"])
def save_img():
    """API endpoint to update user profiles."""
    token_receive = request.cookies.get("mytoken")  # Get token from cookies
    try:
        payload = jwt.decode(token_receive, SECRET_KEY,
                             algorithms=["HS256"])  # Decode JWT
        # Fetch user info from database
        user_info = db.users.find_one({"username": payload["id"]})
        # Get current profile picture path
        file_path = user_info["profile_pic_real"]
        username = payload["id"]  # Get username from token
        # Get new profile name from form data
        name_receive = request.form["name_give"]
        # Get new profile info from form data
        about_receive = request.form["about_give"]
        # Prepare updated profile data
        new_doc = {"profile_name": name_receive, "profile_info": about_receive}
        if "file_give" in request.files:  # Check if a new profile picture is uploaded
            file = request.files["file_give"]  # Get uploaded file
            filename = secure_filename(file.filename)  # Secure the filename
            extension = filename.split(".")[-1]  # Get file extension
            # Construct new file path
            file_path = f"profile_pics/{username}.{extension}"
            file.save("./static/" + file_path)  # Save the file
            # Update profile picture filename
            new_doc["profile_pic"] = filename
            # Update profile picture path
            new_doc["profile_pic_real"] = file_path
        # Update user profile in database
        db.users.update_one({"username": payload["id"]}, {"$set": new_doc})
        # also update user profile in posts collections
        db.posts.update_many({"username": payload["id"]}, {"$set": {
                             "profile_name": name_receive, "profile_pic_real": file_path}})  # Update user profile in posts
        # Return success response
        return jsonify({"result": "success", "msg": "Profile updated!"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        # Redirect to home if token invalid or expired
        return redirect(url_for("home"))


@app.route("/posting", methods=["POST"])
def posting():
    """API endpoint to create a new post."""
    token_receive = request.cookies.get("mytoken")  # Get token from cookies
    try:
        payload = jwt.decode(token_receive, SECRET_KEY,
                             algorithms=["HS256"])  # Decode JWT
        # We should create a new post here
        # Fetch user info from database
        user_info = db.users.find_one({"username": payload["id"]})
        # Get comment from form data
        comment_receive = request.form["comment_give"]
        date_receive = request.form["date_give"]  # Get date from form data
        doc = {
            "username": user_info["username"],
            "profile_name": user_info["profile_name"],
            "profile_pic_real": user_info["profile_pic_real"],
            "comment": comment_receive,
            "date": date_receive,
        }
        db.posts.insert_one(doc)  # Insert new post into database
        # Return success response
        return jsonify({"result": "success", "msg": "Posting successful!"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        # Redirect to home if token invalid or expired
        return redirect(url_for("home"))


@app.route("/get_posts", methods=["GET"])
def get_posts():
    """API endpoint to fetch posts."""
    token_receive = request.cookies.get("mytoken")  # Get token from cookies
    try:
        payload = jwt.decode(token_receive, SECRET_KEY,
                             algorithms=["HS256"])  # Decode JWT

        # Get optional username filter from query params
        username_receive = request.args.get("username_give")
        if username_receive == "":
            # Get latest 20 posts if no user filter
            posts = list(db.posts.find({}).sort("date", -1).limit(20))
        else:
            posts = list(
                db.posts.find({"username": username_receive}
                              ).sort("date", -1).limit(20)
            )  # Get latest 20 posts for the specified user

        for post in posts:
            post["_id"] = str(post["_id"])  # Convert ObjectId to string
            post["count_heart"] = db.likes.count_documents(
                {"post_id": post["_id"], "type": "heart"}
            )  # Count number of hearts for the post
            post["count_star"] = db.likes.count_documents(
                {"post_id": post["_id"], "type": "star"}
            )  # Count number of stars for the post
            post["count_thumbsup"] = db.likes.count_documents(
                {"post_id": post["_id"], "type": "thumbsup"}
            )  # Count number of thumbs ups for the post

            # Check if the post is liked by the logged-in user
            post["heart_by_me"] = bool(
                db.likes.find_one(
                    {"post_id": post["_id"], "type": "heart",
                        "username": payload["id"]}
                )
            )
            post["star_by_me"] = bool(
                db.likes.find_one(
                    {"post_id": post["_id"], "type": "star",
                        "username": payload["id"]}
                )
            )
            post["thumbsup_by_me"] = bool(
                db.likes.find_one(
                    {"post_id": post["_id"], "type": "thumbsup",
                        "username": payload["id"]}
                )
            )

        return jsonify(
            {
                "result": "success",
                "msg": "Successful fetched all posts",
                "posts": posts,
            }
        )  # Return success response with posts data
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        # Redirect to home if token invalid or expired
        return redirect(url_for("home"))


@app.route("/update_like", methods=["POST"])
def update_like():
    """API endpoint to update likes on posts."""
    token_receive = request.cookies.get("mytoken")  # Get token from cookies
    try:
        payload = jwt.decode(token_receive, SECRET_KEY,
                             algorithms=["HS256"])  # Decode JWT
        # We should change the like count for the post here
        # Fetch user info from database
        user_info = db.users.find_one({"username": payload["id"]})
        # Get post ID from form data
        post_id_receive = request.form["post_id_give"]
        # Get like type (heart, star, thumbsup) from form data
        type_receive = request.form["type_give"]
        # Get action (like or unlike) from form data
        action_receive = request.form["action_give"]
        doc = {
            "post_id": post_id_receive,
            "username": user_info["username"],
            "type": type_receive,
        }
        if action_receive == "like":
            db.likes.insert_one(doc)  # Insert like document into database
        else:
            db.likes.delete_one(doc)  # Remove like document from database

        count = db.likes.count_documents(
            {"post_id": post_id_receive, "type": type_receive}
        )  # Count total likes of the specified type for the post
        # Return success response with updated count
        return jsonify({"result": "success", "msg": "updated", "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        # Redirect to home if token invalid or expired
        return redirect(url_for("home"))


@app.route("/about", methods=['GET'])
def about():
    """About page."""
    return render_template('about.html')  # Render about page


@app.route('/secret', methods=['GET'])
def secret():
    """Secret page accessible only to logged-in users."""
    token_receive = request.cookies.get("mytoken")  # Get token from cookies
    try:
        payload = jwt.decode(token_receive, SECRET_KEY,
                             algorithms=["HS256"])  # Decode JWT
        # Fetch user info from database
        user_info = db.users.find_one({"username": payload["id"]})
        # Render secret page with user info
        return render_template('secret.html', user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        # Redirect to home if token invalid or expired
        return redirect(url_for("home"))


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)  # Run the Flask app
