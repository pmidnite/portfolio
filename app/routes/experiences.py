from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson import json_util
from datetime import datetime
from app.models.experiences import Experiences
from app.models.about import About

bp = Blueprint('experience', __name__, url_prefix='/api/experience')

@bp.route('', methods=['GET'])
def fetch_experiences():
    try:
        payload = request.json
        experiences = Experiences.fetch_exact_experience(payload.get("Email"), payload.get("Start Year"))
    except:
        experiences = Experiences.fetch_experience()
    if experiences:
        return json_util.dumps(experiences)
    return jsonify({"Message": "No experience exist currently."})


@bp.route('', methods=["POST", "PATCH"])
@jwt_required()
def insert_or_update_experience():
    experience_payload = request.json
    emails = [x["Email"] for x in experience_payload]
    is_email_exists = list(filter(lambda x: About.fetch_exact_about(payload.get(x)), emails) for payload in experience_payload)
    if is_email_exists:
        Experiences.insert_or_update_experience(experience_payload)
        return jsonify({"message": "Experience inserted/updated Successfully."})
    return jsonify({"message": "Can't add experience since, Email: {0} doesn't exists.".
                    format(experience_payload.get("Email"))})

@bp.route('', methods=["Delete"])
@jwt_required()
def delete_experience():
    del_payload = request.json
    is_exp_exists = Experiences.fetch_exact_experience(del_payload["Email"],
                                                       del_payload.get("Start Year"))
    if is_exp_exists:
        Experiences.delete_experience(del_payload)
        return jsonify({"Message": "Deleted experince: {0} for Email: {1}".format(is_exp_exists,
                                                                                  del_payload["Email"])})
    return jsonify({"Message": "No experience exists for Email: {0}.".format(del_payload.get("Email"))})
