from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from flask import current_app
from app import limiter
from app.utilities.response import APIResponse
from app.utilities.logger import get_logger, log_security_event

logger = get_logger(__name__)

bp = Blueprint("auth", __name__, url_prefix="/get_token")


@bp.route("", methods=["POST"])
@limiter.limit("5 per minute")
def generate_token():
    try:
        body = request.get_json(silent=True) or {}
        userkey = body.get("username")
        passkey = body.get("password")

        if not userkey or not passkey:
            return APIResponse.error("Username and password are required.", status_code=400)

        api_user = current_app.config.get("API_USERNAME")
        api_pass = current_app.config.get("API_PASSWORD")

        if userkey == api_user and passkey == api_pass:
            access_token = create_access_token(identity=userkey)
            logger.info(f"Token generated for user: {userkey}")
            return APIResponse.success(data={"access_token": access_token}, message="Token generated successfully.")

        log_security_event(
            event_type="FAILED_LOGIN",
            description=f"Failed login attempt for username: {userkey}",
            ip_address=request.remote_addr,
            severity="WARNING"
        )
        return APIResponse.unauthorized("Invalid credentials.")
    except Exception as e:
        logger.error(f"Unexpected error in generate_token: {str(e)}")
        return APIResponse.server_error("An unexpected error occurred.")
