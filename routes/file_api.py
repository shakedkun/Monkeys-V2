"""
File API routes.
"""

import os
import io
from datetime import datetime
from flask import Blueprint, request, jsonify, session, send_file

import data_store

file_api = Blueprint("file_api", __name__)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")


def _secure_save(file_storage):
    """Save an uploaded file and return (original_name, saved_name)."""
    original = file_storage.filename or "unknown"
    saved = f"{int(datetime.now().timestamp() * 1000)}-{original}"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_storage.save(os.path.join(UPLOAD_DIR, saved))
    return original, saved


@file_api.route("/api/get_task_files_list", methods=["GET"])
def get_task_files_list():
    task_id = int(request.args.get("task_id", 0))
    task_files = [
        {
            "id": f["id"],
            "uploaded_at": f["uploaded_at"],
            "uploaded_by": f["uploaded_by"],
            "post_id": f["post_id"],
            "file_name": f["file_name"],
            "real_name": f["real_name"],
        }
        for f in data_store.files
        if f["post_id"] == task_id
    ]
    return jsonify(task_files)


@file_api.route("/api/upload_post_image/", methods=["POST"])
@file_api.route("/api/upload_post_image", methods=["POST"])
def upload_post_image():
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "No file provided"}), 400
    _, saved = _secure_save(f)
    return jsonify({"location": saved})


@file_api.route("/api/upload_post_file/", methods=["POST"])
@file_api.route("/api/upload_post_file", methods=["POST"])
def upload_post_file():
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "No file provided"}), 400

    original, saved = _secure_save(f)
    task_id = int(request.form.get("taskid", 0))
    user = session.get("user", {})

    new_file = {
        "id": data_store.get_id("file"),
        "file_name": original,
        "real_name": saved,
        "post_id": task_id,
        "uploaded_by": user.get("id", 0),
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    data_store.files.append(new_file)
    return jsonify({"response": "success"})


@file_api.route("/api/delete_file", methods=["GET"])
def delete_file():
    fid = int(request.args.get("id", 0))
    data_store.files[:] = [f for f in data_store.files if f["id"] != fid]
    return jsonify({"response": "success"})


@file_api.route("/api/upload_pdf_bc/", methods=["POST"])
@file_api.route("/api/upload_pdf_bc", methods=["POST"])
def upload_pdf_bc():
    f = request.files.get("pdf_file")
    if not f:
        return jsonify({"error": "No file provided"}), 400

    original, saved = _secure_save(f)
    task_id = int(request.form.get("taskid", 0))
    user = session.get("user", {})

    new_file = {
        "id": data_store.get_id("file"),
        "file_name": original,
        "real_name": saved,
        "post_id": task_id,
        "uploaded_by": user.get("id", 0),
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    data_store.files.append(new_file)
    return jsonify({"response": "success"})


@file_api.route("/api/download_word_bc/", methods=["GET"])
@file_api.route("/api/download_word_bc", methods=["GET"])
def download_word_bc():
    task_id = int(request.args.get("task_id", 0))
    task = next((p for p in data_store.posts if p["id"] == task_id), None)

    content = (
        f"Task: {task['title']}\n\n{task['content']}\n\nGenerated: {datetime.now().isoformat()}"
        if task
        else "Task not found"
    )

    buf = io.BytesIO(content.encode("utf-8"))
    return send_file(
        buf,
        as_attachment=True,
        download_name=f"task_{task_id}_bc.docx",
        mimetype="application/octet-stream",
    )


@file_api.route("/api/download_archive_file", methods=["GET"])
def download_archive_file():
    file_id = int(request.args.get("file_id", 0))

    archive_file = next(
        (f for f in data_store.archive_files if f["id"] == file_id), None
    )
    if archive_file:
        full_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            archive_file["file_path"],
        )
        if os.path.exists(full_path):
            return send_file(full_path, as_attachment=True)

        # Dummy content if file doesn't exist on disk
        buf = io.BytesIO(
            f"Dummy PDF content for: {archive_file['file_name']}".encode()
        )
        return send_file(
            buf,
            as_attachment=True,
            download_name=archive_file["file_name"],
            mimetype="application/pdf",
        )

    return jsonify({"error": "File not found"}), 404
