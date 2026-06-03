# routes/skills.py
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint
from sqlalchemy.orm import joinedload

from app.utilities.response import APIResponse
from app.utilities.logger import get_logger
from app.utilities.database import db
from app.models.about import About
from app.models.skills import Skills, MappedSkills

logger = get_logger(__name__)

bp = Blueprint("skill", __name__, description='Skill Implementation Logic', url_prefix="/api/skill")


@bp.route("", methods=["GET"])
def fetch_skill():
    skills = Skills.query.all()
    if skills:
        return APIResponse.success(data=[skill.to_dict() for skill in skills])
    return APIResponse.not_found("No skills exist currently.")


@bp.route("", methods=["POST", "PATCH"])
@jwt_required()
def insert_or_update_skill():
    try:
        skill_payload = request.get_json(silent=True)
        if not skill_payload:
            return APIResponse.error("Request body is required.", status_code=400)

        unavailable_column = []
        for payload in skill_payload:
            skill = Skills.query.filter_by(skill_name=payload.get("Skill Name")).first()
            final_obj = skill if skill else Skills()

            for key, value in payload.items():
                attr = key.lower().replace(' ', '_')
                if hasattr(final_obj, attr):
                    setattr(final_obj, attr, value)
                else:
                    unavailable_column.append(key)

            final_obj.save()

        logger.info("Skills inserted/updated successfully.")
        message = "Skill values have been inserted/updated successfully."
        if unavailable_column:
            message += f" Unknown fields ignored: {unavailable_column}"
        return APIResponse.success(message=message)
    except Exception as e:
        logger.error(f"Error inserting/updating skill: {str(e)}")
        return APIResponse.server_error("An error occurred while processing skill data.")


@bp.route("", methods=["DELETE"])
@jwt_required()
def delete_skill():
    try:
        del_payload = request.get_json(silent=True)
        if not del_payload:
            return APIResponse.error("Request body is required.", status_code=400)

        is_exists = Skills.query.filter_by(skill_name=del_payload.get("Skill Name")).first()
        if is_exists:
            is_exists.delete()
            logger.info(f"Skill '{del_payload.get('Skill Name')}' deleted.")
            return APIResponse.deleted(f"Skill '{del_payload.get('Skill Name')}' deleted successfully.")
        return APIResponse.not_found(f"Skill '{del_payload.get('Skill Name')}' does not exist.")
    except Exception as e:
        logger.error(f"Error deleting skill: {str(e)}")
        return APIResponse.server_error("An error occurred while deleting the skill.")


@bp.route("/mapping", methods=["POST", "PATCH"])
@jwt_required()
def insert_or_update_mapped_skill():
    try:
        mapped_payload = request.get_json(silent=True)
        if not mapped_payload:
            return APIResponse.error("Request body is required.", status_code=400)

        about = About.query.filter_by(email=mapped_payload.get('Email')).first()
        if not about:
            return APIResponse.not_found(
                f"Email '{mapped_payload.get('Email')}' does not exist."
            )

        # Fix: scope delete to this user's mappings only (not all rows in the table)
        MappedSkills.query.filter_by(about_id=about.id).delete()
        db.session.flush()

        unavailable_skill = []
        for skill_name in mapped_payload.get("Skill Names", "").split(","):
            skill_name = skill_name.strip()
            if not skill_name:
                continue

            is_skill_exists = Skills.query.filter_by(skill_name=skill_name).first()
            if not is_skill_exists:
                unavailable_skill.append(skill_name)
                continue

            mapped_skill = MappedSkills()
            mapped_skill.about_id = about.id
            mapped_skill.skill_id = is_skill_exists.id
            db.session.add(mapped_skill)

        db.session.commit()
        logger.info(f"Skills mapped for email: {mapped_payload.get('Email')}")

        message = "Skills mapped successfully."
        if unavailable_skill:
            message += f" Unknown skills ignored: {unavailable_skill}"
        return APIResponse.success(message=message)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error mapping skills: {str(e)}")
        return APIResponse.server_error("An error occurred while mapping skills.")


@bp.route("/mapping", methods=["GET"])
def fetch_mapped_skill():
    mapped_skills = MappedSkills.query.all()
    return APIResponse.success(data=[ms.to_dict() for ms in mapped_skills])


@bp.route("/mapping/exact", methods=["GET"])
def fetch_exact_mapped_skill():
    try:
        # Fix N+1: use a single joined query instead of per-row lookups
        about = About.query.first()
        if not about:
            return APIResponse.not_found("No about record found.")

        # Single query: join MappedSkills → Skills for this user
        exact_skills = (
            db.session.query(Skills)
            .join(MappedSkills, MappedSkills.skill_id == Skills.id)
            .filter(MappedSkills.about_id == about.id)
            .order_by(MappedSkills.id.asc())
            .all()
        )

        return APIResponse.success(data=[skill.to_dict() for skill in exact_skills])
    except Exception as e:
        logger.error(f"Error fetching exact mapped skills: {str(e)}")
        return APIResponse.server_error("An error occurred while fetching mapped skills.")


@bp.route("/mapping", methods=["DELETE"])
@jwt_required()
def delete_mapped_skill():
    try:
        del_payload = request.get_json(silent=True)
        if not del_payload:
            return APIResponse.error("Request body is required.", status_code=400)

        about = About.query.filter_by(email=del_payload.get("Email")).first()
        skill = Skills.query.filter_by(skill_name=del_payload.get("Skill Name")).first()

        if not about:
            return APIResponse.not_found(f"Email '{del_payload.get('Email')}' does not exist.")
        if not skill:
            return APIResponse.not_found(f"Skill '{del_payload.get('Skill Name')}' does not exist.")

        is_mapping_exists = MappedSkills.query.filter_by(
            about_id=about.id, skill_id=skill.id
        ).first()

        if is_mapping_exists:
            is_mapping_exists.delete()
            logger.info(
                f"Skill mapping deleted: '{del_payload.get('Skill Name')}' "
                f"for email: '{del_payload.get('Email')}'"
            )
            return APIResponse.deleted(
                f"Skill '{del_payload.get('Skill Name')}' unmapped for '{del_payload.get('Email')}' successfully."
            )
        return APIResponse.not_found(
            f"No mapping exists for email '{del_payload.get('Email')}' "
            f"with skill '{del_payload.get('Skill Name')}'."
        )
    except Exception as e:
        logger.error(f"Error deleting skill mapping: {str(e)}")
        return APIResponse.server_error("An error occurred while deleting the skill mapping.")
