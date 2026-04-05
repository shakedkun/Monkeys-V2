"""
Authentication API routes.
"""

import time
import uuid
from flask import Blueprint, request, jsonify, session

import data_store

auth_api = Blueprint("auth_api", __name__)


@auth_api.route("/api/login_user", methods=["POST"])
def login_user():
    data = request.get_json(force=True, silent=True) or request.form
    username = data.get("username", "")
    password = data.get("password", "")

    user = next(
        (u for u in data_store.users
         if u["username"] == username and u["password"] == password),
        None,
    )

    if not user:
        return jsonify({"response": "Username or password are incorrect."})

    session["user"] = {
        "id": user["id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "privilege": user["privilege"],
        "freedom_date": user["freedom_date"],
    }

    from datetime import date
    today = date.today().isoformat()
    prev_login = user["last_login"] or "first login"
    user["last_login"] = today

    return jsonify({
        "response": "Logged in successfully.",
        "update_last_login_result": f"Last login: {prev_login}",
    })


@auth_api.route("/api/register_user", methods=["POST"])
def register_user():
    data = request.get_json(force=True, silent=True) or request.form
    username = data.get("username", "")
    password = data.get("password", "")
    conpass = data.get("conpass", "")
    email = data.get("email", "")
    full_name = data.get("full_name", "")
    team = data.get("team", "")
    id_number = data.get("id_number", "")
    phone_number = data.get("phone_number", "")
    freedom_date = data.get("freedom_date", "")

    if not username or not password or not email or not full_name:
        return jsonify({"response": "יש למלא את כל השדות."})
    if password != conpass:
        return jsonify({"response": "הסיסמאות אינן תואמות."})
    if any(u["username"] == username for u in data_store.users):
        return jsonify({"response": "שם המשתמש כבר תפוס."})
    if any(u["email"] == email for u in data_store.users):
        return jsonify({"response": "כתובת האימייל כבר קיימת במערכת."})

    new_user = {
        "id": data_store.get_id("user"),
        "username": username,
        "password": password,
        "email": email,
        "full_name": full_name,
        "team": team,
        "id_number": id_number,
        "phone_number": phone_number,
        "freedom_date": freedom_date,
        "privilege": 0,
        "last_login": None,
    }
    data_store.users.append(new_user)
    return jsonify({"response": "success"})


@auth_api.route("/api/send_verification_email", methods=["POST"])
def send_verification_email():
    data = request.get_json(force=True, silent=True) or request.form
    username = data.get("username", "")

    user = next(
        (u for u in data_store.users if u["username"] == username), None
    )
    if not user:
        return jsonify({"response": "User not found."})

    token = str(uuid.uuid4())
    data_store.reset_tokens[token] = {
        "username": user["username"],
        "expires_at": time.time() + 3600,
    }

    print(f"[DUMMY] Password reset token for {username}: {token}")
    print(f"[DUMMY] Reset URL: http://localhost:5000/password_recovery/{token}")

    return jsonify({"response": "success"})


@auth_api.route("/api/reset_password", methods=["POST"])
def reset_password():
    data = request.get_json(force=True, silent=True) or request.form
    token = data.get("token", "")
    password = data.get("password", "")

    entry = data_store.reset_tokens.get(token)
    if not entry or time.time() > entry["expires_at"]:
        data_store.reset_tokens.pop(token, None)
        return jsonify({"response": "Invalid or expired token."})

    user = next(
        (u for u in data_store.users if u["username"] == entry["username"]),
        None,
    )
    if user:
        user["password"] = password
    data_store.reset_tokens.pop(token, None)

    return jsonify({"response": "success"})
