# Routes for skills

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson import json_util
from datetime import datetime
from app.utilities.sql_queries import *
from app.models.about import About
from app.models.skills import Skills, MappedSkills

bp = Blueprint("skill", __name__, url_prefix="/api/skill")

@bp.route("", methods=["GET"])
def fetch_skill():
    skills = Skills.query.all()
    if skills:
        return json_util.dumps(map_class_to_dict(skill) for skill in skills)
    return jsonify({"Message": "No skill exist currently."})

@bp.route("", methods=["POST", "PATCH"])
@jwt_required()
def insert_or_update_skill():
    try:
        skill_payload = request.json
        unavailable_column = []
        for payload in skill_payload:
            skill = Skills.query.filter_by(skill_name=payload.get("Skill Name")).all()
            if skill:
                final_obj = skill[0]
            else:
                final_obj = Skills()
            for key, value in payload.items():
                if hasattr(final_obj, key.lower().replace(' ', '_')):
                    setattr(final_obj, key.lower().replace(' ', '_'), value)
                else:
                    unavailable_column.append(key)
            db.session.add(final_obj)
            db.session.commit()
        if unavailable_column:
            message = " except these values {0} as these column doesn't exists".format(unavailable_column)
            return jsonify({"Message": "Skill values have been Inserted/Updated successfully, " + message})
        return jsonify({"Message": "Skill values have been Inserted/Updated successfully."})
    except Exception as e:
        return jsonify({"Message": "Some exception happened. {0}".format(e)})

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
    try:
        mapped_payload = request.json
        about = About.query.filter_by(email=mapped_payload.get('Email')).one()
        unavailable_skill = []
        if about:
            MappedSkills.query.delete()
            for skill in mapped_payload.get("Skill Names").split(","):
                mapped_skill = MappedSkills()
                mapped_skill.about_id = about.id
                is_skill_exists = Skills.query.filter_by(skill_name=skill.strip()).first()
                if is_skill_exists:
                    is_mapping_exists = MappedSkills.query.filter_by(about_id=about.id, skill_id=is_skill_exists.id).all()
                    if is_mapping_exists:
                        continue
                    mapped_skill.skill_id = is_skill_exists.id
                else:
                    unavailable_skill.append(skill.strip())
                    continue
                db.session.add(mapped_skill)
                db.session.commit()
            if unavailable_skill:
                msg = " except these {0} skills since these doesn't exists.".format(unavailable_skill)
                return jsonify({"message": "Skill Mapped successfully," + msg})
            return jsonify({"message": "Skill Mapped successfully"})
    except Exception as e:
        return jsonify({"Message": "Some error occured. Error: {0}".format(e)})

@bp.route("/mapping", methods=["GET"])
def fetch_mapped_skill():
    mapped_skills = MappedSkills.query.all()
    return json_util.dumps(map_class_to_dict(mapped_skill) for mapped_skill in mapped_skills)


@bp.route("/mapping/exact", methods=["GET"])
def fetch_exact_mapped_skill():
    about = About.query.first()
    mapped_skills = MappedSkills.query.filter_by(about_id=about.id).all()
    exact_skills = []
    for skill in mapped_skills:
        exact_skills.append(Skills.query.filter_by(id=skill.skill_id).first())
    return json_util.dumps(map_class_to_dict(mapped_skill) for mapped_skill in exact_skills)

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
