from flask import Flask, request, jsonify, session,render_template
from pymongo import MongoClient
import os
import uuid
from datetime import datetime, timedelta
from flask_cors import CORS
import jwt
from functools import wraps
import bcrypt
from werkzeug.security import generate_password_hash, check_password_hash




# SECRET_KEY = "asdfghjklq123456ertyuiocbnm56882r"

app = Flask(__name__)
app.secret_key = os.getenv('secret_key')
# CORS(app)
CORS(app, supports_credentials=True)

# -------------------------------
# MongoDB Connection
# -------------------------------
database = MongoClient(os.getenv('database'))

users_db = database["login_users_list"]
user_collection = users_db["user_data"]


# -------------------------------
# Token Authorization
# -------------------------------
# def token_authorization(func):
#     @wraps(func)
#     def data_decode(*args, **kwargs):

#         token = None
#         auth_header = request.headers.get("Authorization")

#         if auth_header:
#             token = auth_header.split(" ")[1]

#         if not token:
#             return jsonify({"msg": "Token not found"}), 401

#         try:
#             user = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
#             user_id = user["user_id"]

#         except jwt.ExpiredSignatureError:
#             return jsonify({"msg": "Token expired. Try again"}), 401

#         except jwt.InvalidTokenError:
#             return jsonify({"msg": "Invalid token"}), 401

#         return func(user_id, *args, **kwargs)

#     return data_decode


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"msg": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return wrapper


# -------------------------------
# Home Route
# -------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to Arun API Backend"
    }), 200


# -------------------------------
# Register API
# -------------------------------
@app.route("/api/register", methods=["POST","GET"])
def register():

    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    hashed_password = generate_password_hash(password)

    if not username or not email or not password:
        return jsonify({"msg": "All fields are required"}), 400

    if user_collection.find_one({"email": email}):
        return jsonify({"msg": "Email already exists"}), 400

    user_collection.insert_one({
        "user_id": str(uuid.uuid4()),
        "username": username,
        "email": email,
        "password": hashed_password,
        "created_at": datetime.now()
    })

    return jsonify({"msg": "User Registered Successfully"}), 201


# -------------------------------
# Login API
# -------------------------------
@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")
    # print(password,"<- pass")
    # print(type(password),"<- pass")

    user = user_collection.find_one({"username": username})
    print(user,"<- data")

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"msg": "Invalid username or Password"}), 401

    # token_data = {
    #     "user_id": user["user_id"],
    #     "exp": datetime.now() + timedelta(hours=1)
    # }

    # token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
    session["user_id"] = user["user_id"]
    session["username"] = user["username"]

    # return jsonify({"token": token})
    return jsonify({"msg":"Login success"})


# -------------------------------
# Protected API Example
# -------------------------------
# @app.route("/api/profile", methods=["GET"])
# @token_authorization
# def profile(user_id):

#     user = user_collection.find_one(
#         {"user_id": user_id},
#         {"_id": 0, "password": 0}
#     )

#     if not user:
#         return jsonify({"msg": "User not found"}), 404

#     return jsonify(user), 200




#session based #

@app.route("/api/profile", methods=["GET"])
@login_required
def profile():
    print(session, "<- session data")
    user_id = session["user_id"]
    print(user_id,"<- hem")

    user = user_collection.find_one(
        {"user_id": user_id},
        {"_id": 0, "password": 0}
    )

    if not user:
        return jsonify({"msg": "User not found"}), 404

    return jsonify(user), 200


@app.route("/api/logout")
def logout():
    session.clear()
    return jsonify({"msg": "Logged out"})

from flask import jsonify

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "API endpoint not found"
    }), 404


# -------------------------------
# Run Server
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)