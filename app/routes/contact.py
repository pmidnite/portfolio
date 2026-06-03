# routes/contact.py
from flask import request, jsonify, current_app
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required
from datetime import datetime
from flask_mail import Message

from app import limiter
from app.config import Config
from app.utilities.response import APIResponse
from app.utilities.mail_config import mail, send_email_async
from app.utilities.logger import get_logger
from app.models.contact import Contact
from app.utilities.validation import validate_contact_payload

logger = get_logger(__name__)

bp = Blueprint("contact", __name__, description="Contact Implementation Logic", url_prefix="/api")


@bp.route('/contact')
class ContactView(MethodView):
    @jwt_required()
    def get(self):
        contacts = Contact.fetch_all_records_dict()
        return APIResponse.success(data=contacts if contacts else [])

    @limiter.limit("3 per minute; 10 per hour")
    def post(self):
        try:
            contact_payload = request.get_json(silent=True)
            if not contact_payload:
                return APIResponse.error("Request body is required.", status_code=400)

            validator = validate_contact_payload(contact_payload)
            if not validator.validate():
                errors = validator.get_errors()
                error_msg = "; ".join([f"{f}: {', '.join(errs)}" for f, errs in errors.items()])
                return APIResponse.error(error_msg, status_code=400)

            # Sanitize inputs to prevent HTML/script injection
            import html
            for field in ['Name', 'Email', 'Company', 'Designation', 'Message']:
                if field in contact_payload and isinstance(contact_payload[field], str):
                    contact_payload[field] = html.escape(contact_payload[field])

            is_already_contacted = Contact.fetch_all_records_dict(email=contact_payload.get('Email'))
            current_datetime = datetime.now()
            unavailable_column = []

            if not is_already_contacted or len(is_already_contacted) < 3:
                new_contact_obj = Contact()
                contact_payload.update({'Contact Date': current_datetime})
            else:
                return APIResponse.error(
                    "You have already messaged 3 times. Wait until I revert back. Thank you!",
                    status_code=429
                )

            for key, value in contact_payload.items():
                attr = key.lower().replace(' ', '_')
                if hasattr(new_contact_obj, attr):
                    setattr(new_contact_obj, attr, value)
                else:
                    unavailable_column.append(key)

            new_contact_obj.save()

            # Get form payload data
            name = contact_payload.get('Name')
            email = contact_payload.get('Email')
            company = contact_payload.get('Company')
            designation = contact_payload.get('Designation')
            message = contact_payload.get('Message')

            app_obj = current_app._get_current_object()

            # Send acknowledgement to sender
            if Config.MAIL_USERNAME and email:
                subject = "Thank you for reaching out to me."
                revert_message = (
                    f"Thank You {name} for your valuable message, "
                    "I will revert back to you soon.\n\nThanks,\nSarfaraz"
                )
                acknowledgement = Message(
                    subject=subject,
                    sender=Config.MAIL_USERNAME,
                    recipients=[email]
                )
                acknowledgement.body = revert_message
                send_email_async(app_obj, acknowledgement)
            else:
                logger.warning("Mail username is not configured; skipping sender acknowledgement email.")

            # Send notification to owner
            recipients = [r for r in [Config.MAIL_USERNAME, Config.MAIL_RECIPIENT] if r]
            if Config.MAIL_USERNAME and recipients:
                subject = "You got a new message from your PORTFOLIO Website."
                notification = Message(
                    subject=subject,
                    sender=Config.MAIL_USERNAME,
                    recipients=recipients
                )
                notification.body = (
                    f"You have got the below message from {name} ({designation}) from {company}\n\n{message}"
                )
                send_email_async(app_obj, notification)
            else:
                logger.warning("Mail username or recipients not configured; skipping owner notification email.")

            if unavailable_column:
                logger.warning(f"Contact message received with unknown fields: {unavailable_column}")

            return APIResponse.success(message="Thank you for your message.")
        except Exception as e:
            # Log the full error server-side but never expose it to the client
            logger.error(f"Error processing contact form: {str(e)}")
            return APIResponse.server_error("Failed to send message. Please try again later.")

    @jwt_required()
    def delete(self):
        try:
            del_payload = request.get_json(silent=True)
            if not del_payload:
                return APIResponse.error("Request body is required.", status_code=400)

            email = del_payload.get('Email')
            contact_date_str = del_payload.get('Contact Date')

            if email and contact_date_str:
                import datetime
                try:
                    contact_date = datetime.datetime.fromisoformat(contact_date_str)
                    contact = Contact.query.filter_by(email=email, contact_date=contact_date).first()
                    if contact:
                        contact.delete()
                        logger.info(f"Contact message deleted for: {email} ({contact_date_str})")
                        return APIResponse.deleted(f"Deleted message from {contact.name} successfully.")
                except Exception as ex:
                    logger.error(f"Error deleting contact using date: {str(ex)}")

            is_contact_exist = Contact.fetch_all_records(email=email, asc=True)
            if is_contact_exist:
                first_contact = is_contact_exist[0]
                first_contact.delete()
                logger.info(f"Contact message deleted for: {first_contact.name}")
                return APIResponse.deleted(f"Deleted message from {first_contact.name} successfully.")
            return APIResponse.not_found(
                f"No message exists from email: {email}"
            )
        except Exception as e:
            logger.error(f"Error deleting contact record: {str(e)}")
            return APIResponse.server_error("An error occurred while deleting the message.")
