# Routes for educations.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
from bson import json_util
from app.utilities.sql_queries import *
from app.models.educations import Education
from app.models.about import About

bp = Blueprint("education", __name__, url_prefix="/api/education")

@bp.route("", methods=["GET"])
def fetch_education():
    educations = Education.query.order_by("start_year").all()
    if educations:
        return json_util.dumps(map_class_to_dict(education) for education in educations)
    else:
        return jsonify({"Message": "No data exists."})

@bp.route("", methods=["POST", "PATCH"])
@jwt_required()
def insert_or_update_education():
    try:
        education_payload = request.json
        is_email_exists = About.query.filter_by(email=education_payload.get('Email')).first()
        current_datetime = datetime.now()
        unavailable_column = []
        if is_email_exists:
            is_exists = Education.query.filter_by(email=education_payload.get('Email'),
                                                  start_year=education_payload.get("Start Year")).first()
            if is_exists:
                education_payload.update({'Updated Date': current_datetime})
            else:
                education_payload.update({'Created Date': current_datetime, 'Updated Date': current_datetime})
                new_education_obj = Education()

            final_obj = is_exists or new_education_obj
            for key, value in education_payload.items():
                if hasattr(final_obj, key.lower().replace(' ', '_')):
                    setattr(final_obj, key.lower().replace(' ', '_'), value)
                else:
                    unavailable_column.append(key)
            db.session.add(final_obj)
            db.session.commit()
            if unavailable_column:
                message = " except these values {0} as these column doesn't exists".format(unavailable_column)
                return jsonify({"Message": "Education inserted/updated successfully" + message})
            return jsonify({"Message": "Education inserted/updated successfully"})
        else:
            msg = "Can't add education since, Email: {0} doesn't exists."
            return jsonify({"message": msg.format(education_payload.get("Email"))})
    except Exception as er:
        return jsonify({"Message": "Missing some data while filling education form: {0}.".format(er)})

@bp.route("", methods=["DELETE"])
@jwt_required()
def delete_education():
    try:
        del_payload = request.json
        is_exists = Education.query.filter_by(email=del_payload.get('Email')).\
            order_by(Education.start_year.asc()).first()
        if is_exists:
            db.session.delete(is_exists)
            db.session.commit()
            return jsonify({"message": "Education: {0} deleted successfully".format(is_exists)})
        else:
            return jsonify({"message": "No education exists for Email: {0}.".format(del_payload.get("Email"))})
    except Exception as e:
        return jsonify({"Message": "Missing/Wrong data while delete education: {0}.".format(e)})
