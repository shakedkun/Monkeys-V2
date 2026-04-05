"""
Archive API routes.
"""

import os
from flask import Blueprint, request, jsonify

import data_store

archive_api = Blueprint("archive_api", __name__)

ARCHIVE_UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "uploads", "archive"
)


@archive_api.route("/api/get_sites", methods=["GET"])
def get_sites():
    search_string = request.args.get("search_string", "")
    filtered = list(data_store.sites)
    if search_string:
        q = search_string.lower()
        filtered = [s for s in filtered if q in s["name"].lower()]
    return jsonify(filtered)


@archive_api.route("/api/get_site_tasks", methods=["GET"])
def get_site_tasks():
    site_id = int(request.args.get("site_id", 0))
    search_string = request.args.get("search_string", "")

    filtered = [t for t in data_store.archive_tasks if t["site_id"] == site_id]
    if search_string:
        q = search_string.lower()
        filtered = [t for t in filtered if q in t["name"].lower()]

    return jsonify(filtered)


@archive_api.route("/api/get_site_task_files", methods=["GET"])
def get_site_task_files():
    task_id = int(request.args.get("task_id", 0))
    filtered = [f for f in data_store.archive_files if f["task_id"] == task_id]
    return jsonify(filtered)


@archive_api.route("/api/add_archive_task", methods=["POST"])
def add_archive_task():
    data = request.get_json(force=True, silent=True) or request.form

    new_task = {
        "id": data_store.get_id("archive_task"),
        "name": data.get("name", ""),
        "site_id": int(data.get("site_id", 0)),
    }
    data_store.archive_tasks.append(new_task)
    return jsonify({"response": "success"})


@archive_api.route("/api/add_file_archive_task", methods=["POST"])
def add_file_archive_task():
    f = request.files.get("pdf_file")
    file_name = request.form.get("file_name", "")
    site_id = int(request.form.get("site_id", 0))
    task_id = int(request.form.get("task_id", 0))
    special_type = request.form.get("special_type", "")

    saved_name = "dummy.pdf"
    if f:
        from datetime import datetime
        saved_name = f"{int(datetime.now().timestamp() * 1000)}-{f.filename}"
        os.makedirs(ARCHIVE_UPLOAD_DIR, exist_ok=True)
        f.save(os.path.join(ARCHIVE_UPLOAD_DIR, saved_name))

    new_file = {
        "id": data_store.get_id("archive_file"),
        "file_name": file_name or (f.filename if f else "unknown"),
        "file_path": f"uploads/archive/{saved_name}",
        "site_id": site_id,
        "task_id": task_id,
        "special_type": special_type,
    }
    data_store.archive_files.append(new_file)

    return jsonify({
        "database_response": "success",
        "files_response": "success",
    })
