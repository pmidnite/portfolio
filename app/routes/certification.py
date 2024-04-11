from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson import json_util
from app.utilities.sql_utils import *
from app.models.certification import Certification

bp = Blueprint('certification', __name__, url_prefix='/api/certification')

@bp.route('', methods=['GET'])
def fetch_certification():
    certs = Certification.query.all()
    if certs:
        return json_util.dumps(map_class_to_dict(cert) for cert in certs)
    else:
        return jsonify({"Message": "No certification exists."})

@bp.route('', methods=['POST', 'PATCH'])
@jwt_required()
def insert_or_update_certification():
    certification_payload = request.json
    is_exists = Certification.query.filter_by(cert_name=certification_payload.get('Cert Name')).first()
    unavailable_column = []

    final_obj = is_exists or Certification()
    for key, value in certification_payload.items():
        if hasattr(final_obj, key.lower().replace(' ', '_')):
            setattr(final_obj, key.lower().replace(' ', '_'), value)
        else:
            unavailable_column.append(key)
    db.session.add(final_obj)
    db.session.commit()
    if unavailable_column:
        message = " except these values {0} as these column doesn't exists".format(unavailable_column)
        return jsonify({"Message": "Certification inserted/updated successfully" + message})
    return jsonify({'Message': 'Certification inserted/updated successfully'})

@bp.route('', methods=['DELETE'])
@jwt_required()
def delete_certification():
    try:
        del_payload = request.json
        is_exists = Certification.query.filter_by(cert_name=del_payload.get('Cert Name')).first()
        if is_exists:
            db.session.delete(is_exists)
            db.session.commit()
            return jsonify({'Message': 'Certification deleted successfully'})
        else:
            return jsonify({'Message': "Cert Name: {0} doesn't exists.".format(del_payload.get('Cert Name'))})
    except:
        return jsonify({"Message": "Some exception occured."})
