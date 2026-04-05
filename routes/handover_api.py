"""
Handover API routes.
"""

from flask import Blueprint, request, jsonify

import data_store

handover_api = Blueprint("handover_api", __name__)


@handover_api.route("/transfer-tasks-titles", methods=["GET"])
def transfer_tasks_titles():
    titles = [p["title"] for p in data_store.posts]
    return jsonify(titles)


@handover_api.route("/send-handover-email", methods=["POST"])
def send_handover_email():
    data = request.get_json(force=True, silent=True) or request.form
    tasks = data.get("tasks", [])
    general_comment = data.get("general_comment", "")
    questions = data.get("questions", "")

    print("[DUMMY] Handover email sent:")
    print(f"  Tasks: {tasks}")
    print(f"  General comment: {general_comment}")
    print(f"  Questions: {questions}")

    return jsonify({"response": "Handover email sent successfully."}), 200
