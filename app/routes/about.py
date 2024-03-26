# routes/about.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
from bson import json_util
from app.utilities.sql_queries import *
from app.models.about import About

bp = Blueprint('about', __name__, url_prefix='/api/about')

@bp.route('', methods=['GET'])
def fetch_about():
    about = About.query.first()
    if about:
        return json_util.dumps(map_class_to_dict(about))
    else:
        return jsonify({"Message": "No data exists."})

@bp.route('', methods=['POST', 'PATCH'])
@jwt_required()
def insert_or_update_about():
    about_payload = request.json
    is_exists = About.query.filter_by(email=about_payload.get('Email')).first()
    current_datetime = datetime.now()
    unavailable_column = []
    if is_exists:
        about_payload.update({'Updated Date': current_datetime})
    else:
        about_payload.update({'Created Date': current_datetime, 'Updated Date': current_datetime})
        new_about_obj = About()

    final_obj = is_exists or new_about_obj
    for key, value in about_payload.items():
        if hasattr(final_obj, key.lower().replace(' ', '_')):
            setattr(final_obj, key.lower().replace(' ', '_'), value)
        else:
            unavailable_column.append(key)
    db.session.add(final_obj)
    db.session.commit()
    if unavailable_column:
        message = " except these values {0} as these column doesn't exists".format(unavailable_column)
        return jsonify({"Message": "About inserted/updated successfully" + message})
    return jsonify({'message': 'About inserted/updated successfully'})

@bp.route('', methods=['DELETE'])
@jwt_required()
def delete_about():
    del_payload = request.json
    is_exists = About.query.filter_by(email=del_payload.get('Email')).first()
    if is_exists:
        db.session.delete(is_exists)
        db.session.commit()
        return jsonify({'message': 'About deleted successfully'})
    else:
        return jsonify({'message': "Email: {0} doesn't exists.".format(del_payload.get('Email'))})
