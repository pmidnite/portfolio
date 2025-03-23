# Routes for contact

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson import json_util
from datetime import datetime
from flask_mail import Message
from app.config import Config
from app.utilities.sql_utils import *
from app.utilities.mail_config import mail
from app.models.contact import Contact

bp = Blueprint("contact", __name__, url_prefix="/api/contact")

@bp.route("", methods=["GET"])
@jwt_required()
def fetch_contact():
    contacts = Contact.query.all()
    if contacts:
        return json_util.dumps(map_class_to_dict_all(contact) for contact in contacts)
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

        # Get form payload data
        name = contact_payload.get('Name')
        email = contact_payload.get('Email')
        company = contact_payload.get('Company')
        designation = contact_payload.get('Designation')
        message = contact_payload.get('Message')

        # Send email to sender
        subject = "Thank you for reaching out to me."
        revert_message = "Thank You {0} for your valuable message, I will revert back to you soon.\n\nThanks,\nSarfaraz".format(name)
        acknowledgement = Message(subject=subject, sender=Config.MAIL_USERNAME, recipients=[email])
        acknowledgement.body = revert_message
        mail.send(acknowledgement)

        # Recieve a notification regarding the message
        subject = "You got a new message from your PORTFOLIO Website."
        notification = Message(subject=subject, sender=Config.MAIL_USERNAME, recipients=[Config.MAIL_USERNAME, Config.MAIL_RECIPIENT])
        notification.body = "You have got the below message from {0}({1}) from {2}\n\n{3}".\
                            format(name, designation, company, message)
        mail.send(notification)

        if unavailable_column:
            message = " except these values {0} as these column doesn't exists".format(unavailable_column)
            return jsonify({"Message": "Thank you for your message." + message})
        return jsonify({"Message": "Thank you for your message."})

    except:
        return jsonify({"Message": "Some Error Occured."})

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
