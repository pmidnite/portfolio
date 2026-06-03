# __init__.py
from flask import Flask, render_template
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .config import Config
from app.utilities.response import APIResponse

jwt = JWTManager()
migrate = Migrate()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"],
    storage_uri="memory://"
)

from app.models import about, contact, educations,\
                       experiences, skills, testimonials, certification
from app.routes import about, educations, skills,\
                       experiences, testimonials, contact, generate_token,\
                       certification
from app.utilities.database import create_database, db
from app.utilities.mail_config import mail_config
from app.utilities.logger import get_logger


# Initialize logger for this module
logger = get_logger(__name__)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Fix: logger.info() does not accept a dict as a second positional argument
    # Use extra= keyword or log a formatted string instead
    logger.info(
        "Flask application initialization started",
        extra={"app_name": app.name, "config": app.config.get('ENV', 'unknown')}
    )

    jwt.init_app(app)
    limiter.init_app(app)
    create_database(app)
    mail_config(app)

    # Initialize Flask-Migrate for DB schema migrations
    migrate.init_app(app, db)

    @app.errorhandler(429)
    def ratelimit_handler(e):
        from flask import request
        from app.utilities.logger import log_security_event
        ip_address = request.remote_addr or get_remote_address()
        endpoint = request.path
        description = getattr(e, 'description', "Rate limit exceeded")
        log_security_event(
            event_type="RATE_LIMIT_EXCEEDED",
            description=f"Rate limit exceeded on {endpoint}: {description}",
            ip_address=ip_address,
            severity="WARNING"
        )
        return APIResponse.error(message="Too many requests. Please try again later.", status_code=429)

    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        from flask import request
        from app.utilities.logger import log_security_event
        ip_address = request.remote_addr or get_remote_address()
        log_security_event(
            event_type="JWT_UNAUTHORIZED",
            description=f"Missing or unauthorized JWT token: {callback}",
            ip_address=ip_address,
            severity="WARNING"
        )
        return APIResponse.unauthorized(callback)

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        from flask import request
        from app.utilities.logger import log_security_event
        ip_address = request.remote_addr or get_remote_address()
        log_security_event(
            event_type="JWT_INVALID",
            description=f"Invalid JWT token: {callback}",
            ip_address=ip_address,
            severity="WARNING"
        )
        return APIResponse.error(message="Invalid token", status_code=401)

    @jwt.expired_token_loader
    def expired_token_response(jwt_header, jwt_payload):
        from flask import request
        from app.utilities.logger import log_security_event
        ip_address = request.remote_addr or get_remote_address()
        log_security_event(
            event_type="JWT_EXPIRED",
            description=f"Expired JWT token. Payload: {jwt_payload}",
            ip_address=ip_address,
            severity="WARNING"
        )
        return APIResponse.error(message="Token has expired", status_code=401)

    @app.route("/")
    @app.route("/index")
    def index():
        logger.info("Index route accessed")
        return render_template('index.html')

    @app.route("/admin")
    def admin():
        logger.info("Admin portal route accessed")
        return render_template('admin.html')

    app.register_blueprint(about.bp)
    app.register_blueprint(educations.bp)
    app.register_blueprint(skills.bp)
    app.register_blueprint(experiences.bp)
    app.register_blueprint(testimonials.bp)
    app.register_blueprint(contact.bp)
    app.register_blueprint(certification.bp)
    app.register_blueprint(generate_token.bp)

    logger.info(
        "Flask application initialization completed successfully",
        extra={"registered_blueprints": [bp.name for bp in app.blueprints.values()]}
    )

    return app
