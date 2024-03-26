# Routes for contact

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson import json_util
from datetime import datetime
from app.utilities.sql_queries import *
from app.models.contact import Contact

bp = Blueprint("contact", __name__, url_prefix="/api/contact")

@bp.route("", methods=["GET"])
@jwt_required()
def fetch_contact():
    contacts = Contact.query.all()
    if contacts:
        return json_util.dumps(map_class_to_dict(contact) for contact in contacts)
    else:
        return jsonify({"Message": "No data exists."})

@bp.route("", methods=["POST", "PATCH"])
def insert_or_update_contact():
    try:
        contact_payload = request.json
        is_already_contacted = Contact.query.filter_by(email=contact_payload.get('Email')).all()
        current_datetime = datetime.now()
        unavailable_column = []
        if not is_already_contacted or len(is_already_contacted) < 3:
            new_contact_obj = Contact()
            contact_payload.update({'Contact Date': current_datetime})
        else:
            return jsonify({"Message": "You have already messaged 3 times. Wait untill I revert back. Thank You!!!"})

        for key, value in contact_payload.items():
            if hasattr(new_contact_obj, key.lower().replace(' ', '_')):
                setattr(new_contact_obj, key.lower().replace(' ', '_'), value)
            else:
                unavailable_column.append(key)
        db.session.add(new_contact_obj)
        db.session.commit()
        if unavailable_column:
            message = " except these values {0} as these column doesn't exists".format(unavailable_column)
            return jsonify({"Message": "Thank you for your message." + message})
        return jsonify({"Message": "Thank you for your message."})

    except:
        return jsonify({"Message": "Missing some data while filling contact form."})

@bp.route("", methods=["DELETE"])
@jwt_required()
def delete_contact():
    try:
        del_payload = request.json
        is_contact_exist = Contact.query.filter_by(email=del_payload.get('Email')).order_by(Contact.contact_date.asc()).all()
        if is_contact_exist:
            db.session.delete(is_contact_exist[0])
            db.session.commit()
            return jsonify({"Message": "Deleted message: {0} successfully.".format(is_contact_exist[0])})
        else:
            return jsonify({"Message": "No message exists for the given user: {0}({1})".
                            format(del_payload.get("Name"), del_payload.get("Email"))})
    except Exception as e:
        return jsonify({"Message": "Missing/Wrong data while delete message: {0}.".format(e)})
