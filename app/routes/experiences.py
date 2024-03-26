from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson import json_util
from datetime import datetime
from app.utilities.sql_queries import *
from app.models.experiences import Experiences
from app.models.about import About

bp = Blueprint('experience', __name__, url_prefix='/api/experience')

@bp.route('', methods=['GET'])
def fetch_experiences():
    try:
        payload = request.json
        experiences = Experiences.query.filter_by(email=payload.get("Email"), start_year=payload.get("Start Year")).all()
    except:
        experiences = Experiences.query.order_by(Experiences.start_year.desc()).all()
    if experiences:
        return json_util.dumps(map_class_to_dict(experience) for experience in experiences)
    return jsonify({"Message": "No experience exist currently."})


@bp.route('', methods=["POST", "PATCH"])
@jwt_required()
def insert_or_update_experience():
    experience_payload = request.json
    unavailable_column = []
    for payload in experience_payload:
        is_email_exists = About.query.filter_by(email=payload.get('Email')).first()
        if is_email_exists:
            is_exists = Experiences.query.filter_by(email=payload.get('Email'),
                                                    start_year=payload.get("Start Year")).first()
            final_obj = is_exists or Experiences()
            for key, value in payload.items():
                if hasattr(final_obj, key.lower().replace(' ', '_')):
                    setattr(final_obj, key.lower().replace(' ', '_'), value)
                else:
                    unavailable_column.append(key)
            db.session.add(final_obj)
            db.session.commit()
            continue
        else:
            return jsonify({"message": "Can't add experience since, Email: {0} doesn't exists.".
                            format(payload.get("Email"))})
    if unavailable_column:
        message = " except these values {0} as these column doesn't exists".format(unavailable_column)
        return jsonify({"Message": "Experience inserted/updated Successfully." + message})
    return jsonify({"Message": "Experience inserted/updated Successfully."})

@bp.route('', methods=["Delete"])
@jwt_required()
def delete_experience():
    # TODO: MYSQL changes
    del_payload = request.json
    is_exp_exists = Experiences.fetch_exact_experience(del_payload["Email"],
                                                       del_payload.get("Start Year"))
    if is_exp_exists:
        Experiences.delete_experience(del_payload)
        return jsonify({"Message": "Deleted experince: {0} for Email: {1}".format(is_exp_exists,
                                                                                  del_payload["Email"])})
    return jsonify({"Message": "No experience exists for Email: {0}.".format(del_payload.get("Email"))})
