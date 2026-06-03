# routes/certification.py
from flask import request, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required

from app.utilities.response import APIResponse
from app.utilities.logger import get_logger
from app.models.certification import Certification

logger = get_logger(__name__)

bp = Blueprint('certification', __name__, description='Certification Implementation Logic', url_prefix='/api')


@bp.route('/certification')
class CertificationView(MethodView):
    def get(self):
        certs = Certification.fetch_all_records_dict()
        if certs:
            return APIResponse.success(data=certs)
        return APIResponse.not_found("No certifications exist.")

    @jwt_required()
    def post(self):
        try:
            certification_payload = request.get_json(silent=True)
            if not certification_payload:
                return APIResponse.error("Request body is required.", status_code=400)

            is_exists = Certification.filter_by_cert_name(cert_name=certification_payload.get('Cert Name'))
            unavailable_column = []

            final_obj = is_exists if is_exists else Certification()
            for key, value in certification_payload.items():
                attr = key.lower().replace(' ', '_')
                if hasattr(final_obj, attr):
                    setattr(final_obj, attr, value)
                else:
                    unavailable_column.append(key)

            final_obj.save()
            logger.info(f"Certification saved: {certification_payload.get('Cert Name')}")

            message = "Certification inserted/updated successfully."
            if unavailable_column:
                message += f" Unknown fields ignored: {unavailable_column}"
            return APIResponse.success(message=message)
        except Exception as e:
            logger.error(f"Error processing certification: {str(e)}")
            return APIResponse.server_error("An error occurred while processing certification data.")

    @jwt_required()
    def delete(self):
        try:
            del_payload = request.get_json(silent=True)
            if not del_payload:
                return APIResponse.error("Request body is required.", status_code=400)

            is_exists = Certification.filter_by_cert_name(cert_name=del_payload.get('Cert Name'))
            if is_exists:
                is_exists.delete()
                logger.info(f"Certification deleted: {del_payload.get('Cert Name')}")
                return APIResponse.deleted("Certification deleted successfully.")
            return APIResponse.not_found(f"Cert Name '{del_payload.get('Cert Name')}' does not exist.")
        except Exception as e:
            logger.error(f"Error deleting certification: {str(e)}")
            return APIResponse.server_error("An error occurred while deleting the certification.")
