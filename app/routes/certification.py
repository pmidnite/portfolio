from flask import Blueprint, request, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required
from app.utilities.utils import *
from app.models.certification import Certification

bp = Blueprint('certification', __name__, description='Certification Implementation Logic', url_prefix='/api')


@bp.route('/certification')
class CertificationView(MethodView):
    def get(self):
        certs = Certification.fetch_all_records_dict()
        if certs:
            return certs
        return jsonify({"Message": "No certification exists."})

    @jwt_required()
    def post(self):
        certification_payload = request.get_json()
        is_exists = Certification.filter_by_cert_name(cert_name=certification_payload.get('Cert Name'))
        unavailable_column = []

        final_obj = is_exists or Certification()
        for key, value in certification_payload.items():
            if hasattr(final_obj, key.lower().replace(' ', '_')):
                setattr(final_obj, key.lower().replace(' ', '_'), value)
            else:
                unavailable_column.append(key)

        final_obj.save()

        if unavailable_column:
            message = " except these values {0} as these column doesn't exists".format(unavailable_column)
            return jsonify({"Message": "Certification inserted/updated successfully" + message})

        return jsonify({'Message': 'Certification inserted/updated successfully'})

    @jwt_required()
    def delete(self):
        try:
            del_payload = request.get_json()
            is_exists = Certification.filter_by_cert_name(cert_name=del_payload.get('Cert Name'))
            if is_exists:
                is_exists.delete()
                return jsonify({'Message': 'Certification deleted successfully'})
            else:
                return jsonify({'Message': "Cert Name: {0} doesn't exists.".format(del_payload.get('Cert Name'))})
        except Exception as e:
            return jsonify({"Message": "Some exception occurred: {}".format(str(e))})
