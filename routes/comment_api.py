"""
Comment API routes.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify, session

import data_store

comment_api = Blueprint("comment_api", __name__)


@comment_api.route("/api/get_comments_for_task", methods=["GET"])
def get_comments_for_task():
    task_id = int(request.args.get("task_id", 0))
    task_comments = [
        {
            "id": c["id"],
            "content": c["content"],
            "edited": c["edited"],
            "data_posted": c["data_posted"],
            "userID": c["userID"],
            "comment_id": c["id"],
        }
        for c in data_store.comments
        if c["post_id"] == task_id
    ]
    return jsonify(task_comments)


@comment_api.route("/api/add_comment", methods=["POST"])
def add_comment():
    data = request.get_json(force=True, silent=True) or request.form
    user = session.get("user", {})

    new_comment = {
        "id": data_store.get_id("comment"),
        "content": data.get("content", ""),
        "post_id": int(data.get("post_id", 0)),
        "user_id": user.get("id", 0),
        "userID": user.get("username", "anonymous"),
        "data_posted": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "edited": [],
    }
    data_store.comments.append(new_comment)
    return jsonify({"response": "success", "post_id": new_comment["post_id"]})


@comment_api.route("/api/edit_comment", methods=["POST"])
def edit_comment():
    data = request.get_json(force=True, silent=True) or request.form
    cid = int(data.get("comment_id", 0))
    comment = next((c for c in data_store.comments if c["id"] == cid), None)

    if comment:
        comment["edited"].append(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        comment["content"] = data.get("content", comment["content"])

    return jsonify({
        "response": "success",
        "post_id": int(data.get("post_id", 0)),
    })


@comment_api.route("/api/delete_comment", methods=["GET"])
def delete_comment():
    cid = int(request.args.get("id", 0))
    data_store.comments[:] = [
        c for c in data_store.comments if c["id"] != cid
    ]
    return jsonify({"response": "success"})
