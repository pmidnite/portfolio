from flask import Blueprint, request, jsonify
from bson import json_util
from datetime import datetime
from app.models.testimonials import Testimonials


bp = Blueprint("testimonial", __name__, url_prefix="/api/testimonial")


@bp.route('', methods=["GET"])
def fetch_testimonials():
    try:
        testimonial_payload = request.json
        testimonials = Testimonials.fetch_exact_testimonial({"Name": testimonial_payload.get("Name")})
    except:
        testimonials = Testimonials.fetch_testimonial()
    return json_util.dumps(testimonials)

@bp.route('', methods=["POST", "PATCH"])
def insert_or_update_testimonial():
    testimonial_payload = request.json
    Testimonials.insert_or_update_testimonial(testimonial_payload)
    return jsonify({"Message": "Thank You for your testimony about me, I will review and approve it soon."})

@bp.route('', methods=["DELETE"])
def delete_testimonial():
    del_payload = request.json
    is_testimony_exists = Testimonials.fetch_exact_testimonial(del_payload.get("Name"), del_payload.get("Company"))
    if is_testimony_exists:
        Testimonials.delete_testimonial(del_payload)
        return jsonify({"Message": "Testimony of user {0} from company {1} is deleted successfully.".
                        format(del_payload.get("Name"), del_payload.get("Company"))})
    return jsonify({"Message": "Testimony of user {0} from company {1} doesn't exists.".
                    format(del_payload.get("Name"), del_payload.get("Company"))})
    
@bp.route('/review', methods=["PATCH"])
def review_testimony():
    review_payload = request.json
    is_testimony_exists = Testimonials.fetch_exact_testimonial(review_payload.get("Name"), review_payload.get("Company"))
    is_review_col = review_payload.get("Reviewed")
    if is_testimony_exists and is_review_col:
        Testimonials.review_testimonial(review_payload.get("Name"), review_payload.get("Company"),
                                        is_review_col)
        return jsonify({"Message": "Testimony of user {0} from company {1} is reviewed.".
                        format(review_payload.get("Name"), review_payload.get("Company"))})
    elif not is_testimony_exists:
        return jsonify({"Message": "Testimony of user {0} from company {1} doesn't exists.".
                        format(review_payload.get("Name"), review_payload.get("Company"))})
    elif not is_review_col:
        return jsonify({"Message": "Testimony of user {0} from company {1} is not reviewed.".
                        format(review_payload.get("Name"), review_payload.get("Company"))})
        