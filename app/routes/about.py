# routes/about.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
from bson import json_util
from app.models.about import About

bp = Blueprint('about', __name__, url_prefix='/api/about')

@bp.route('', methods=['GET'])
def fetch_about():
    about = About.fetch_about()
    return json_util.dumps(about)

@bp.route('', methods=['POST', 'PATCH'])
@jwt_required()
def insert_or_update_about():
    about_payload = request.json
    is_exists = About.fetch_exact_about(about_payload.get('Email'))
    current_datetime = datetime.now()
    if is_exists:
        about_payload.update({'Updated Date': current_datetime})
    else:
        about_payload.update({'Created Date': current_datetime, 'Updated Date': current_datetime})
    About.insert_or_update(about_payload)
    return jsonify({'message': 'About inserted/updated successfully'})

@bp.route('', methods=['DELETE'])
@jwt_required()
def delete_about():
    del_payload = request.json
    is_exists = About.fetch_exact_about(del_payload.get('Email'))
    if is_exists:
        About.delete_about(del_payload)
        return jsonify({'message': 'About deleted successfully'})
    else:
        return jsonify({'message': "Email: {0} doesn't exists.".format(del_payload.get('Email'))})
