# Routes for skills

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson import json_util
from datetime import datetime
from app.models.skills import Skills, MappedSkills

bp = Blueprint("skill", __name__, url_prefix="/api/skill")

@bp.route("", methods=["GET"])
def fetch_skill():
    skills = Skills.fetch_skills()
    return json_util.dumps(skills)

@bp.route("", methods=["POST", "PATCH"])
@jwt_required()
def insert_or_update_skill():
    skill_payload = request.json
    is_exists = Skills.fetch_skills()
    Skills.insert_or_update_skill(skill_payload)
    return jsonify({"message": "Skill inserted/updated successfully"})

@bp.route("", methods=["DELETE"])
@jwt_required()
def delete_skill():
    del_payload = request.json
    is_exists = Skills.fetch_exact_skill(del_payload.get("Skill Name"))
    if is_exists:
        Skills.delete_skill(del_payload)
        return jsonify({"message": "Skill -> {0} deleted successfully".format(is_exists[0])})
    else:
        return jsonify({"message": "Skill -> {0} doesn't exists".format(del_payload.get('Skill Name'))})

@bp.route("/mapping", methods=["POST", "PATCH"])
@jwt_required()
def insert_or_update_mapped_skill():
    mapped_payload = request.json
    MappedSkills.insert_or_update_mapped_skill(mapped_payload)
    return jsonify({"message": "Skill Mapping inserted/updated successfully"})

@bp.route("/mapping", methods=["GET"])
def fetch_mapped_skill():
    mapped_skills = MappedSkills.fetch_mapped_skill()
    return json_util.dumps(mapped_skills)

@bp.route("/mapping", methods=["DELETE"])
@jwt_required()
def delete_mapped_skill():
    del_payload = request.json
    is_mapping_exists = MappedSkills.fetch_exact_mapped_skill(del_payload["Email"])
    if is_mapping_exists:
        MappedSkills.delete_mapped_skill(del_payload["Email"])
        return jsonify({"Message": "Deleted the Skill mapping successfully for Email: {0}".
            format(del_payload["Email"])})
    return jsonify({"Message": "No Mapping exists to delete for the Email: {0}".format(del_payload["Email"])})
