"""
Task / Post API routes.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify, session

import data_store

task_api = Blueprint("task_api", __name__)

POSTS_PER_PAGE = 10


@task_api.route("/api/get_tasks", methods=["GET"])
def get_tasks():
    content = request.args.get("content", "")
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    category_id = request.args.get("category_id", "")
    location = request.args.get("location", "")
    post_id = request.args.get("post_id", "")
    current_page = request.args.get("current_page", "1")

    filtered = list(data_store.posts)

    if content:
        q = content.lower()
        filtered = [
            p for p in filtered
            if q in p["title"].lower() or q in p["content"].lower()
        ]

    if start_date:
        filtered = [
            p for p in filtered if p["date_posted"].split(" ")[0] >= start_date
        ]

    if end_date:
        filtered = [
            p for p in filtered if p["date_posted"].split(" ")[0] <= end_date
        ]

    if category_id:
        cat_id = int(category_id)
        filtered = [p for p in filtered if p["category_id"] == cat_id]

    if location:
        filtered = [p for p in filtered if p["location"] == location]

    if post_id:
        pid = int(post_id)
        filtered = [p for p in filtered if p["id"] == pid]

    # Sort descending by date
    filtered.sort(key=lambda p: p["date_posted"], reverse=True)

    # Pagination
    page = int(current_page or 1)
    total = len(filtered)
    pages_number = max(1, -(-total // POSTS_PER_PAGE))  # ceil division
    start = (page - 1) * POSTS_PER_PAGE
    tasks_on_page = filtered[start: start + POSTS_PER_PAGE]

    return jsonify({
        "tasks_on_page": [
            {
                "content": p["content"],
                "category_id": p["category_id"],
                "title": p["title"],
                "id": p["id"],
                "username": p["username"],
                "location": p["location"],
                "date_posted": p["date_posted"],
                "edited": p["edited"],
            }
            for p in tasks_on_page
        ],
        "pages_number": pages_number,
        "current_page": page,
    })


@task_api.route("/api/get_task", methods=["GET"])
def get_task():
    task_id = int(request.args.get("task_id", 0))
    task = next((p for p in data_store.posts if p["id"] == task_id), None)

    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({
        "id": task["id"],
        "title": task["title"],
        "content": task["content"],
        "category_id": task["category_id"],
        "location": task["location"],
        "username": task["username"],
        "date_posted": task["date_posted"],
        "edited": task["edited"],
    })


@task_api.route("/api/add_post", methods=["POST"])
def add_post():
    data = request.get_json(force=True, silent=True) or request.form
    user = session.get("user", {})

    new_post = {
        "id": data_store.get_id("post"),
        "title": data.get("title", ""),
        "content": data.get("content", ""),
        "category_id": int(data.get("category_id", 0)),
        "location": data.get("location", ""),
        "username": user.get("username", "anonymous"),
        "user_id": user.get("id", 0),
        "date_posted": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "edited": None,
    }
    data_store.posts.append(new_post)
    return jsonify({"response": "success", "post_id": new_post["id"]})


@task_api.route("/api/edit_post", methods=["POST"])
def edit_post():
    data = request.get_json(force=True, silent=True) or request.form
    pid = int(data.get("post_id", 0))
    post = next((p for p in data_store.posts if p["id"] == pid), None)

    if not post:
        return jsonify({"error": "Post not found"}), 404

    post["title"] = data.get("title", post["title"])
    post["content"] = data.get("content", post["content"])
    post["edited"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return jsonify({"response": "success", "post_id": post["id"]})


@task_api.route("/api/delete_post", methods=["GET"])
def delete_post():
    pid = int(request.args.get("id", 0))
    idx = next((i for i, p in enumerate(data_store.posts) if p["id"] == pid), None)

    if idx is not None:
        data_store.posts.pop(idx)
        data_store.comments[:] = [
            c for c in data_store.comments if c["post_id"] != pid
        ]
        data_store.files[:] = [
            f for f in data_store.files if f["post_id"] != pid
        ]

    return jsonify({"response": "success"})


@task_api.route("/api/change_post_category", methods=["POST"])
def change_post_category():
    data = request.get_json(force=True, silent=True) or request.form
    pid = int(data.get("post_id", 0))
    post = next((p for p in data_store.posts if p["id"] == pid), None)

    if post:
        post["category_id"] = int(data.get("new_category_id", post["category_id"]))

    return jsonify({"response": "success"})
