# routes/experiences.py
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint
from datetime import datetime

from app.utilities.response import APIResponse
from app.utilities.logger import get_logger
from app.models.experiences import Experiences
from app.models.about import About

logger = get_logger(__name__)

bp = Blueprint('experience', __name__, description='Experience Implementation Logic', url_prefix='/api/experience')


@bp.route('', methods=['GET'])
def fetch_experiences():
    try:
        payload = request.get_json(silent=True)
        if payload and (payload.get("Email") or payload.get("Start Year")):
            experiences = Experiences.query.filter_by(
                email=payload.get("Email"),
                start_year=payload.get("Start Year")
            ).all()
        else:
            experiences = Experiences.query.order_by(Experiences.start_year.desc()).all()
    except Exception as e:
        logger.error(f"Error fetching experiences: {str(e)}")
        return APIResponse.server_error("An error occurred while fetching experiences.")

    if experiences:
        return APIResponse.success(data=[exp.to_dict() for exp in experiences])
    return APIResponse.not_found("No experience records exist.")


@bp.route('', methods=["POST", "PATCH"])
@jwt_required()
def insert_or_update_experience():
    try:
        experience_payload = request.get_json(silent=True)
        if not experience_payload:
            return APIResponse.error("Request body is required.", status_code=400)

        unavailable_column = []
        for payload in experience_payload:
            is_email_exists = About.query.filter_by(email=payload.get('Email')).first()
            if not is_email_exists:
                return APIResponse.not_found(
                    f"Cannot add experience — email '{payload.get('Email')}' does not exist."
                )

            is_exists = Experiences.query.filter_by(
                email=payload.get('Email'),
                start_year=payload.get("Start Year")
            ).first()
            final_obj = is_exists if is_exists else Experiences()

            for key, value in payload.items():
                attr = key.lower().replace(' ', '_')
                if hasattr(final_obj, attr):
                    setattr(final_obj, attr, value)
                else:
                    unavailable_column.append(key)

            final_obj.save()

        logger.info("Experience records inserted/updated successfully.")
        message = "Experience inserted/updated successfully."
        if unavailable_column:
            message += f" Unknown fields ignored: {unavailable_column}"
        return APIResponse.success(message=message)
    except Exception as e:
        logger.error(f"Error inserting/updating experience: {str(e)}")
        return APIResponse.server_error("An error occurred while processing experience data.")


@bp.route('', methods=["DELETE"])
@jwt_required()
def delete_experience():
    try:
        del_payload = request.get_json(silent=True)
        if not del_payload:
            return APIResponse.error("Request body is required.", status_code=400)

        is_exp_exists = Experiences.query.filter_by(
            email=del_payload.get('Email'),
            start_year=del_payload.get("Start Year")
        ).first()

        if is_exp_exists:
            is_exp_exists.delete()
            logger.info(f"Experience deleted for email: {del_payload.get('Email')}")
            return APIResponse.deleted("Experience deleted successfully.")
        return APIResponse.not_found(
            f"No experience exists for email '{del_payload.get('Email')}' "
            f"with start year '{del_payload.get('Start Year')}'."
        )
    except Exception as e:
        logger.error(f"Error deleting experience: {str(e)}")
        return APIResponse.server_error("An error occurred while deleting the experience.")
