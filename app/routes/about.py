# routes/about.py
from flask import request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint
from datetime import datetime

from app.utilities.response import APIResponse
from app.utilities.validation import validate_about_data
from app.utilities.logger import get_logger
from app.models.about import About

logger = get_logger(__name__)

bp = Blueprint('about', __name__, description='About Implementation Logic', url_prefix='/api')


@bp.route('/about')
class AboutView(MethodView):
    def get(self):
        about = About.fetch_first_record_dict()
        if about:
            return APIResponse.success(data=about)
        return APIResponse.not_found("No about data exists.")

    @jwt_required()
    def post(self):
        about_payload = request.get_json(silent=True)
        if not about_payload:
            return APIResponse.error("Request body is required.", status_code=400)

        # Validate input
        validator = validate_about_data(about_payload)
        if not validator.validate():
            return APIResponse.validation_error(validator.get_errors())

        is_exists = About.filter_by_email(email=about_payload.get('Email'))
        current_datetime = datetime.now()
        unavailable_column = []

        if is_exists:
            about_payload.update({'Updated Date': current_datetime})
        else:
            about_payload.update({'Created Date': current_datetime, 'Updated Date': current_datetime})

        # Fix: always determine final_obj correctly — no UnboundLocalError
        final_obj = is_exists if is_exists else About()

        for key, value in about_payload.items():
            attr = key.lower().replace(' ', '_')
            if hasattr(final_obj, attr):
                setattr(final_obj, attr, value)
            else:
                unavailable_column.append(key)

        final_obj.save()
        logger.info(f"About record saved for email: {about_payload.get('Email')}")

        message = "About inserted/updated successfully."
        if unavailable_column:
            message += f" Unknown fields ignored: {unavailable_column}"
        return APIResponse.success(message=message)

    @jwt_required()
    def delete(self):
        try:
            del_payload = request.get_json(silent=True)
            if not del_payload:
                return APIResponse.error("Request body is required.", status_code=400)

            is_exists = About.filter_by_email(email=del_payload.get('Email'))
            if is_exists:
                is_exists.delete()
                logger.info(f"About record deleted for email: {del_payload.get('Email')}")
                return APIResponse.deleted("About deleted successfully.")
            return APIResponse.not_found(f"Email '{del_payload.get('Email')}' does not exist.")
        except Exception as e:
            logger.error(f"Error deleting about record: {str(e)}")
            return APIResponse.server_error("An error occurred while deleting the record.")
