"""
Bakarim API routes.
"""

from flask import Blueprint, request, jsonify

import data_store

bakarim_api = Blueprint("bakarim_api", __name__)


@bakarim_api.route("/get-bakarim", methods=["GET"])
def get_bakarim():
    return jsonify(data_store.bakarim)


@bakarim_api.route("/get-bakar", methods=["GET"])
def get_bakar():
    bakar_id = int(request.args.get("bakar_id", 0))
    result = [b for b in data_store.bakarim if b["id"] == bakar_id]
    return jsonify(result)


@bakarim_api.route("/create-bakar", methods=["POST"])
def create_bakar():
    data = request.get_json(force=True, silent=True) or request.form

    new_bakar = {
        "id": data_store.get_id("bakar"),
        "full_name": data.get("full_name", ""),
        "t_number": data.get("t_number", ""),
    }
    data_store.bakarim.append(new_bakar)

    return jsonify({
        "message": "Bakar created successfully.",
        "bakar": new_bakar,
    }), 201


@bakarim_api.route("/update-bakar", methods=["PUT"])
def update_bakar():
    data = request.get_json(force=True, silent=True) or request.form
    bid = int(data.get("bakar_id", 0))
    bakar = next((b for b in data_store.bakarim if b["id"] == bid), None)

    if not bakar:
        return jsonify({"message": "Bakar not found."}), 404

    bakar["full_name"] = data.get("full_name", bakar["full_name"])
    bakar["t_number"] = data.get("t_number", bakar["t_number"])

    return jsonify({"message": "Bakar updated successfully.", "bakar": bakar}), 200


@bakarim_api.route("/delete-bakar", methods=["DELETE"])
def delete_bakar():
    bakar_id = int(
        request.args.get("bakar_id", 0)
        or (request.get_json(force=True, silent=True) or {}).get("bakar_id", 0)
    )
    idx = next(
        (i for i, b in enumerate(data_store.bakarim) if b["id"] == bakar_id), None
    )

    if idx is None:
        return jsonify({"massage": "Bakar not found."}), 404

    data_store.bakarim.pop(idx)
    # Note: "massage" typo preserved from original spec
    return jsonify({"massage": "Bakar deleted successfully."})
