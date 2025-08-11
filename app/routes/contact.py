# Routes for contact

from flask import Blueprint, request, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required
from datetime import datetime
from flask_mail import Message
from app.config import Config
from app.utilities.utils import *
from app.utilities.mail_config import mail
from app.models.contact import Contact

bp = Blueprint("contact", __name__, description="Contact Implementation Logic", url_prefix="/api")


@bp.route('/contact')
class ContactView(MethodView):
    def get(self):
        contacts = Contact.fetch_all_records_dict()
        if contacts:
            return contacts
        return jsonify({"Message": "No contact message exists."}), 404

    def post(self):
        try:
            contact_payload = request.get_json()
            is_already_contacted = Contact.fetch_all_records_dict(email=contact_payload.get('Email'))
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

            new_contact_obj.save()

            # Get form payload data
            name = contact_payload.get('Name')
            email = contact_payload.get('Email')
            company = contact_payload.get('Company')
            designation = contact_payload.get('Designation')
            message = contact_payload.get('Message')

            # Send email to sender
            subject = "Thank you for reaching out to me."
            revert_message = "Thank You {0} for your valuable message, I will revert back to you soon.\n\nThanks,\nSarfaraz".format(name)
            acknowledgement = Message(subject=subject,
                sender=Config.MAIL_USERNAME,
                recipients=[email])
            acknowledgement.body = revert_message
            mail.send(acknowledgement)

            # Recieve a notification regarding the message
            subject = "You got a new message from your PORTFOLIO Website."
            notification = Message(subject=subject,
                sender=Config.MAIL_USERNAME,
                recipients=[Config.MAIL_USERNAME, Config.MAIL_RECIPIENT])
            notification.body = "You have got the below message from {0}({1}) from {2}\n\n{3}".\
                                format(name, designation, company, message)
            mail.send(notification)

            if unavailable_column:
                logging.warning("Message recieved with these extra column {0} as these column doesn't exists".\
                    format(unavailable_column))
            return jsonify({"Message": "Thank you for your message."}), 200
        except Exception as e:
            return jsonify({"Message": f"Failed to send message. Please try again later. {e}"}), 400

    @jwt_required()
    def delete(self):
        try:
            del_payload = request.get_json()
            is_contact_exist = Contact.fetch_all_records(email=del_payload.get('Email'), asc=True)
            if is_contact_exist:
                first_contact = is_contact_exist[0]
                is_contact_exist[0].delete()
                return jsonify({"Message": "Deleted message from {0} successfully.".format(first_contact.name)})
            else:
                return jsonify({"Message": "No message exists from this mail id: {0}".
                                format(del_payload.get("Email"))}), 404
        except Exception as e:
            return jsonify({"Message": "Missing/Wrong data while delete message: {0}.".format(e)})
