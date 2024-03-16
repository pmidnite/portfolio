# Routes for skills

from flask import Blueprint, request, jsonify
from bson import json_util
from datetime import datetime
from app.models.skills import Skills

bp = Blueprint("skill", __name__, url_prefix="/api/skill")

@bp.route("", methods=["GET"])
def fetch_skill():
    skills = Skills.fetch_skills()
    return json_util.dumps(skills)

@bp.route("", methods=["POST", "PATCH"])
def insert_or_update_skill():
    skill_payload = request.json
    is_exists = Skills.fetch_skills()
    updated_skill_payload = list(map(lambda x: x.update({'Updated Date': datetime.now()})))
    Skills.insert_or_update_skill(updated_skill_payload)
    return jsonify({"message": "Skill inserted/updated successfully"})

@bp.route("", methods=["DELETE"])
def delete_skill():
    del_payload = request.json
    is_exists = Skills.fetch_exact_skill(del_payload.get("Skill Name"))
    if is_exists:
        Skills.delete_skill(del_payload)
        return jsonify({"message": "Skill -> {0} deleted successfully".format(is_exists[0])})
    else:
        return jsonify({"message": "Skill -> {0} doesn't exists".format(del_payload.get('Skill Name'))})
