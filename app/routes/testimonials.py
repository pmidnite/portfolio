from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson import json_util
from datetime import datetime
from app.models.testimonials import Testimonials


bp = Blueprint("testimonial", __name__, url_prefix="/api/testimonial")


@bp.route('', methods=["GET"])
def fetch_testimonials():
    try:
        testimonial_payload = request.json
        testimonials = Testimonials.fetch_exact_testimonial(testimonial_payload.get("Name"),
                                                            testimonial_payload.get("Email"))
    except:
        all_testimonials = Testimonials.fetch_testimonial()
        testimonials = list(filter(lambda x: x['Reviewed'] == "Y", all_testimonials))
        # testimonials = [testimony for testimony in testimonials if testimony.get("Reveiwed") == "Y"]
    return json_util.dumps(testimonials)

@bp.route('', methods=["POST", "PATCH"])
# @jwt_required()
def insert_or_update_testimonial():
    testimonial_payload = request.json
    Testimonials.insert_or_update_testimonial(testimonial_payload)
    return jsonify({"Message": "Thank You for your testimony about me, I will review and approve it soon."})

@bp.route('', methods=["DELETE"])
@jwt_required()
def delete_testimonial():
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
    is_testimony_exists = Testimonials.fetch_exact_testimonial(review_payload.get("Name"), review_payload.get("Email"))
    is_review_col = review_payload.get("Reviewed")
    if is_testimony_exists and is_review_col:
        Testimonials.review_testimonial(review_payload.get("Name"), review_payload.get("Email"),
                                        is_review_col)
        return jsonify({"Message": "Testimony of user {0} from company {1} is reviewed.".
                        format(review_payload.get("Name"), review_payload.get("Email"))})
    elif not is_testimony_exists:
        return jsonify({"Message": "Testimony of user {0} from company {1} doesn't exists.".
                        format(review_payload.get("Name"), review_payload.get("Email"))})
    elif not is_review_col:
        return jsonify({"Message": "Testimony of user {0} from company {1} is not reviewed.".
                        format(review_payload.get("Name"), review_payload.get("Email"))})
