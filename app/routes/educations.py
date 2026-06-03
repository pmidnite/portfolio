# routes/educations.py
from flask import request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint
from datetime import datetime

from app.utilities.response import APIResponse
from app.utilities.logger import get_logger
from app.models.educations import Education
from app.models.about import About

logger = get_logger(__name__)

bp = Blueprint("education", __name__, description='Education Implementation Logic', url_prefix="/api")


@bp.route('/education')
class EducationView(MethodView):
    def get(self):
        educations = Education.query.order_by(Education.start_year.desc()).all()
        if educations:
            return APIResponse.success(data=[edu.to_dict() for edu in educations])
        return APIResponse.not_found("No education data exists.")

    @jwt_required()
    def post(self):
        try:
            education_payload = request.get_json(silent=True)
            if not education_payload:
                return APIResponse.error("Request body is required.", status_code=400)

            is_email_exists = About.query.filter_by(email=education_payload.get('Email')).first()
            if not is_email_exists:
                return APIResponse.not_found(
                    f"Cannot add education — email '{education_payload.get('Email')}' does not exist."
                )

            current_datetime = datetime.now()
            unavailable_column = []

            is_exists = Education.query.filter_by(
                email=education_payload.get('Email'),
                start_year=education_payload.get("Start Year")
            ).first()

            if is_exists:
                education_payload.update({'Updated Date': current_datetime})
            else:
                education_payload.update({'Created Date': current_datetime, 'Updated Date': current_datetime})

            # Fix: always determine final_obj correctly — no UnboundLocalError
            final_obj = is_exists if is_exists else Education()

            for key, value in education_payload.items():
                attr = key.lower().replace(' ', '_')
                if hasattr(final_obj, attr):
                    setattr(final_obj, attr, value)
                else:
                    unavailable_column.append(key)

            final_obj.save()
            logger.info(f"Education record saved for email: {education_payload.get('Email')}")

            message = "Education inserted/updated successfully."
            if unavailable_column:
                message += f" Unknown fields ignored: {unavailable_column}"
            return APIResponse.success(message=message)
        except Exception as e:
            logger.error(f"Error inserting/updating education: {str(e)}")
            return APIResponse.server_error("An error occurred while processing education data.")

    @jwt_required()
    def delete(self):
        try:
            del_payload = request.get_json(silent=True)
            if not del_payload:
                return APIResponse.error("Request body is required.", status_code=400)

            is_exists = Education.query.filter_by(email=del_payload.get('Email'))\
                .order_by(Education.start_year.asc()).first()
            if is_exists:
                is_exists.delete()
                logger.info(f"Education record deleted for email: {del_payload.get('Email')}")
                return APIResponse.deleted(f"Education record deleted successfully.")
            return APIResponse.not_found(
                f"No education exists for email: '{del_payload.get('Email')}'."
            )
        except Exception as e:
            logger.error(f"Error deleting education record: {str(e)}")
            return APIResponse.server_error("An error occurred while deleting the education record.")
