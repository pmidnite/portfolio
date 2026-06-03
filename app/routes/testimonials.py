# routes/testimonials.py
from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint
from flask_mail import Message

from app.config import Config
from app.utilities.response import APIResponse
from app.utilities.mail_config import mail, send_email_async
from app.utilities.logger import get_logger
from app.models.testimonials import Testimonials
from app.utilities.validation import validate_testimonial_payload

logger = get_logger(__name__)

bp = Blueprint("testimonial", __name__, description='Testimonial Implementation Logic', url_prefix="/api/testimonial")


@bp.route('', methods=["GET"])
def fetch_testimonials():
    try:
        testimonial_payload = request.get_json(silent=True)
        if testimonial_payload and testimonial_payload.get("Email"):
            testimonials = Testimonials.query.filter_by(
                email=testimonial_payload.get("Email")
            ).all()
        else:
            # Public endpoint: return only reviewed testimonials
            testimonials = Testimonials.query.filter_by(reviewed=True).all()
    except Exception as e:
        logger.error(f"Error fetching testimonials: {str(e)}")
        return APIResponse.server_error("An error occurred while fetching testimonials.")

    if testimonials:
        return APIResponse.success(data=[t.to_dict() for t in testimonials])
    return APIResponse.not_found("No reviewed testimonials found.")


@bp.route('/all', methods=["GET"])
@jwt_required()
def fetch_all_testimonials():
    testimonials = Testimonials.query.all()
    if testimonials:
        return APIResponse.success(data=[t.to_dict() for t in testimonials])
    return APIResponse.not_found("No testimonials found.")


@bp.route('', methods=["POST", "PATCH"])
def insert_or_update_testimonial():
    try:
        testimonial_payload = request.get_json(silent=True)
        if not testimonial_payload:
            return APIResponse.error("Request body is required.", status_code=400)

        validator = validate_testimonial_payload(testimonial_payload)
        if not validator.validate():
            errors = validator.get_errors()
            error_msg = "; ".join([f"{f}: {', '.join(errs)}" for f, errs in errors.items()])
            return APIResponse.error(error_msg, status_code=400)

        unavailable_column = []
        testimony = Testimonials.query.filter_by(email=testimonial_payload.get("Email")).all()

        # New testimonials always start as unreviewed (False)
        testimonial_payload.update({"Reviewed": False})

        final_obj = testimony[0] if testimony else Testimonials()

        for key, value in testimonial_payload.items():
            attr = key.lower().replace(' ', '_')
            if hasattr(final_obj, attr):
                setattr(final_obj, attr, value)
            else:
                unavailable_column.append(key)

        final_obj.save()

        # Get form payload data
        name = testimonial_payload.get('Name')
        email = testimonial_payload.get('Email')
        company = testimonial_payload.get('Company')
        designation = testimonial_payload.get('Designation')
        message = testimonial_payload.get('Message')

        app_obj = current_app._get_current_object()

        # Send acknowledgement to submitter
        if Config.MAIL_USERNAME and email:
            subject = "Thank you for your testimonial."
            revert_message = (
                f"Thank You {name} for your valuable testimonial. "
                "You will be able to see it on my website once I approve it.\n\nThanks,\nSarfaraz"
            )
            acknowledgement = Message(
                subject=subject,
                sender=Config.MAIL_USERNAME,
                recipients=[email]
            )
            acknowledgement.body = revert_message
            send_email_async(app_obj, acknowledgement)
        else:
            logger.warning("Mail username is not configured; skipping sender testimonial acknowledgement email.")

        # Send notification to owner
        recipients = [r for r in [Config.MAIL_USERNAME, Config.MAIL_RECIPIENT] if r]
        if Config.MAIL_USERNAME and recipients:
            subject = "You got a new testimonial from your PORTFOLIO Website."
            notification = Message(
                subject=subject,
                sender=Config.MAIL_USERNAME,
                recipients=recipients
            )
            notification.body = (
                f"You have got the below testimonial from {name} ({designation}) from {company}\n\n{message}"
            )
            send_email_async(app_obj, notification)
        else:
            logger.warning("Mail username or recipients not configured; skipping owner testimonial notification email.")

        if unavailable_column:
            logger.warning(f"Testimonial received with unknown fields: {unavailable_column}")

        return APIResponse.success(
            message="Thank you for your testimonial. I will review and approve it soon."
        )
    except Exception as e:
        logger.error(f"Error processing testimonial: {str(e)}")
        return APIResponse.server_error("An error occurred while processing your testimonial.")


@bp.route('', methods=["DELETE"])
@jwt_required()
def delete_testimonial():
    try:
        del_payload = request.get_json(silent=True)
        if not del_payload:
            return APIResponse.error("Request body is required.", status_code=400)

        is_testimony_exists = Testimonials.query.filter_by(
            name=del_payload.get("Name"),
            email=del_payload.get("Email")
        ).first()

        if is_testimony_exists:
            is_testimony_exists.delete()
            logger.info(
                f"Testimonial deleted for {del_payload.get('Name')} ({del_payload.get('Email')})"
            )
            return APIResponse.deleted(
                f"Testimonial from {del_payload.get('Name')} deleted successfully."
            )
        return APIResponse.not_found(
            f"Testimonial from {del_payload.get('Name')} ({del_payload.get('Email')}) does not exist."
        )
    except Exception as e:
        logger.error(f"Error deleting testimonial: {str(e)}")
        return APIResponse.server_error("An error occurred while deleting the testimonial.")


@bp.route('/review', methods=["PATCH"])
@jwt_required()
def review_testimony():
    try:
        review_payload = request.get_json(silent=True)
        if not review_payload:
            return APIResponse.error("Request body is required.", status_code=400)

        is_testimony_exists = Testimonials.query.filter_by(
            email=review_payload.get("Email")
        ).first()

        if not is_testimony_exists:
            return APIResponse.not_found(
                f"Testimonial for '{review_payload.get('Email')}' does not exist."
            )

        reviewed_to = review_payload.get("Reviewed")
        if reviewed_to is None:
            return APIResponse.error(
                f"'Reviewed' field is required to update testimonial review status.",
                status_code=400
            )

        # Reviewed field is now a boolean — accept True/False directly
        if not isinstance(reviewed_to, bool):
            return APIResponse.error("'Reviewed' must be a boolean (true or false).", status_code=400)

        if is_testimony_exists.reviewed == reviewed_to:
            status = "already reviewed" if reviewed_to else "already not reviewed"
            return APIResponse.success(
                message=f"Testimonial for '{review_payload.get('Email')}' is {status}."
            )

        is_testimony_exists.reviewed = reviewed_to
        is_testimony_exists.save()
        status = "approved" if reviewed_to else "unapproved"
        logger.info(f"Testimonial for '{review_payload.get('Email')}' {status}.")
        return APIResponse.success(
            message=f"Testimonial for '{review_payload.get('Email')}' has been {status}."
        )
    except Exception as e:
        logger.error(f"Error reviewing testimonial: {str(e)}")
        return APIResponse.server_error("An error occurred while updating testimonial review status.")
