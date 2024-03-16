# Routes for educations.py
from flask import Blueprint, request, jsonify
from datetime import datetime
from bson import json_util
from app.models.educations import Education
from app.models.about import About

bp = Blueprint("education", __name__, url_prefix="/api/education")

@bp.route("", methods=["GET"])
def fetch_education():
    education = Education.fetch_education()
    return json_util.dumps(education)

@bp.route("", methods=["POST", "PATCH"])
def insert_or_update_education():
    education_payload = request.json
    is_email_exists = About.fetch_exact_about(education_payload.get("Email"))
    if is_email_exists:
        is_exists = Education.fetch_exact_education(education_payload.get("Email"),
                                                    education_payload.get("Start Year"))
        current_datetime = datetime.now()
        if is_exists:
            education_payload.update({"Updated Date": current_datetime})
        else:
            education_payload.update({"Created Date": current_datetime, "Updated Date": current_datetime})
        Education.insert_or_update_education(education_payload)
        return jsonify({"message": "Education inserted/updated successfully"})
    else:
        msg = "Can't add education since, Email: {0} doesn't exists."
        return jsonify({"message": msg.format(education_payload.get("Email"))})

@bp.route("", methods=["DELETE"])
def delete_education():
    del_payload = request.json
    is_exists = Education.fetch_exact_education(del_payload.get("Email"))
    if is_exists:
        Education.delete_education(del_payload)
        return jsonify({"message": "Education: {0} deleted successfully".format(is_exists[0])})
    else:
        return jsonify({"message": "No education exists for Email: {0}.".format(del_payload.get("Email"))})
