# Routes for contact

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson import json_util
from datetime import datetime
from app.models.contact import Contact

bp = Blueprint("contact", __name__, url_prefix="/api/contact")

@bp.route("", methods=["GET"])
@jwt_required()
def fetch_contact():
    contacts = Contact.fetch_contact()
    return json_util.dumps(contacts)

@bp.route("", methods=["POST", "PATCH"])
def insert_or_update_contact():
    try:
        contact_payload = request.json
        is_already_contacted = Contact.fetch_exact_contact(contact_payload.get("Email"))
        if not is_already_contacted or len(is_already_contacted) < 3:
            contact_payload.update({"Contact Date": datetime.now()})
            Contact.insert_contact(contact_payload)
            return jsonify({"Message": "Thank you for your message."})
        else:
            return jsonify({"Message": "You have already messaged 3 times. Wait untill I revert back. Thank You!!!"})
    except:
        return jsonify({"Message": "Missing some data while filling contact form."})

@bp.route("", methods=["DELETE"])
@jwt_required()
def delete_contact():
    try:
        del_payload = request.json
        is_contact_exist = Contact.fetch_exact_contact(del_payload.get("Email"))
        if is_contact_exist:
            Contact.delete_contact(del_payload)
            return jsonify({"Message": "Deleted message: {0} successfully.".format(is_contact_exist[0])})
        else:
            return jsonify({"Message": "No message exists for the given user: {0}({1})".
                            format(del_payload.get("Name"), del_payload.get("Email"))})
    except:
        return jsonify({"Message": "Missing/Wrong data while delete message."})
