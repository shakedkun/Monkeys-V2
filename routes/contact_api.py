"""
Contact API routes.
"""

from flask import Blueprint, request, jsonify

import data_store

contact_api = Blueprint("contact_api", __name__)

CONTACTS_PER_PAGE = 10


@contact_api.route("/api/get_contacts", methods=["GET"])
def get_contacts():
    search_string = request.args.get("search_string", "")
    current_page = request.args.get("current_page", "1")

    filtered = list(data_store.contacts)

    if search_string:
        q = search_string.lower()
        filtered = [
            c
            for c in filtered
            if q in c["first_name"].lower()
            or q in c["last_name"].lower()
            or q in c["phone_number"]
            or q in c["role"].lower()
            or q in c["site"].lower()
        ]

    page = int(current_page or 1)
    total = len(filtered)
    pages_number = max(1, -(-total // CONTACTS_PER_PAGE))
    start = (page - 1) * CONTACTS_PER_PAGE
    contacts_on_page = filtered[start: start + CONTACTS_PER_PAGE]

    return jsonify({
        "contacts_on_page": contacts_on_page,
        "pages_number": pages_number,
        "current_page": page,
    })


@contact_api.route("/api/add_contact", methods=["POST"])
def add_contact():
    data = request.get_json(force=True, silent=True) or request.form

    new_contact = {
        "id": data_store.get_id("contact"),
        "first_name": data.get("first_name", ""),
        "last_name": data.get("last_name", ""),
        "phone_number": data.get("phone_number", ""),
        "role": data.get("role", ""),
        "site": data.get("site", ""),
    }
    data_store.contacts.append(new_contact)
    return jsonify({"response": "success"})


@contact_api.route("/api/edit_contact", methods=["POST"])
def edit_contact():
    data = request.get_json(force=True, silent=True) or request.form
    cid = int(data.get("contact_id", 0))
    contact = next((c for c in data_store.contacts if c["id"] == cid), None)

    if contact:
        contact["first_name"] = data.get("first_name", contact["first_name"])
        contact["last_name"] = data.get("last_name", contact["last_name"])
        contact["phone_number"] = data.get("phone_number", contact["phone_number"])
        contact["role"] = data.get("role", contact["role"])
        contact["site"] = data.get("site", contact["site"])

    return jsonify({"response": "success"})


@contact_api.route("/api/delete_contact", methods=["GET"])
def delete_contact():
    cid = int(request.args.get("id", 0))
    data_store.contacts[:] = [c for c in data_store.contacts if c["id"] != cid]
    return jsonify({"response": "success"})
