from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson import json_util
from datetime import datetime
from app.utilities.sql_queries import *
from app.models.testimonials import Testimonials


bp = Blueprint("testimonial", __name__, url_prefix="/api/testimonial")


@bp.route('', methods=["GET"])
def fetch_testimonials():
    try:
        testimonial_payload = request.json
        testimonials = Testimonials.query.filter_by(email=testimonial_payload.get("Email")).all()
    except:
        testimonials = Testimonials.query.filter_by(reviewed='Y').all()
    if testimonials:
        return json_util.dumps(map_class_to_dict(testimony) for testimony in testimonials)
    else:
        return jsonify({"Message": "No Testimony found."})

@bp.route('', methods=["POST", "PATCH"])
# @jwt_required()
def insert_or_update_testimonial():
    try:
        testimonial_payload = request.json
        unavailable_column = []
        testimony = Testimonials.query.filter_by(email=testimonial_payload.get("Email")).all()
        testimonial_payload.update({"Reviewed": "N"})
        if testimony:
            final_obj = testimony[0]
        else:
            final_obj = Testimonials()
        for key, value in testimonial_payload.items():
            if hasattr(final_obj, key.lower().replace(' ', '_')):
                setattr(final_obj, key.lower().replace(' ', '_'), value)
            else:
                unavailable_column.append(key)

        db.session.add(final_obj)
        db.session.commit()
        if unavailable_column:
            message = " except these values {0} as these column doesn't exists".format(unavailable_column)
            return jsonify({"Message": "Your Testimony has been recieved," + message})
        return jsonify({"Message": "Thank You for your testimony about me, I will review and approve it soon."})
    except Exception as e:
        return jsonify({"Message": "Some exception happened. {0}".format(e)})

@bp.route('', methods=["DELETE"])
@jwt_required()
def delete_testimonial():
    # TODO: Fix for Mysql changes
    del_payload = request.json
    is_testimony_exists = Testimonials.fetch_exact_testimonial(del_payload.get("Name"), del_payload.get("Email"))
    if is_testimony_exists:
        Testimonials.delete_testimonial(del_payload)
        return jsonify({"Message": "Testimony of user {0} from company {1} is deleted successfully.".
                        format(del_payload.get("Name"), del_payload.get("Email"))})
    return jsonify({"Message": "Testimony of user {0} from company {1} doesn't exists.".
                    format(del_payload.get("Name"), del_payload.get("Email"))})

@bp.route('/review', methods=["PATCH"])
@jwt_required()
def review_testimony():
    review_payload = request.json
    is_testimony_exists = Testimonials.query.filter_by(email=review_payload.get("Email")).all()
    is_review_col = review_payload.get("Reviewed")
    if is_testimony_exists and is_review_col:
        is_testimony_exists[0].reviewed = "Y"
        db.session.add(is_testimony_exists[0])
        db.session.commit()
        return jsonify({"Message": "Testimony of user {0} is reviewed.".
                        format(review_payload.get("Email"))})
    elif not is_testimony_exists:
        return jsonify({"Message": "Testimony of user {0} doesn't exists.".
                        format(review_payload.get("Email"))})
    elif not is_review_col:
        return jsonify({"Message": "Testimony of user {0} is not reviewed due to unavailibity of review column.".
                        format(review_payload.get("Email"))})
