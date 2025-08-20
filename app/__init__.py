# __init__.py
from flask import Flask, render_template
from flask_jwt_extended import JWTManager
from .config import Config
from app.models import about, contact, educations,\
                       experiences, skills, testimonials, certification
from app.routes import about, educations, skills,\
                       experiences, testimonials, contact, generate_token,\
                       certification
from app.utilities.database import create_database
from app.utilities.mail_config import mail_config
from app.utilities.logger import get_logger

# Initialize logger for this module
logger = get_logger(__name__)

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize logging first
    logger.info("Flask application initialization started", {
        "app_name": app.name,
        "config": app.config.get('ENV', 'unknown')
    })

    jwt.init_app(app)
    create_database(app)
    mail_config(app)

    @app.route("/")
    @app.route("/index")
    def index():
        logger.info("Index route accessed")
        return render_template('index.html')

    app.register_blueprint(about.bp)
    app.register_blueprint(educations.bp)
    app.register_blueprint(skills.bp)
    app.register_blueprint(experiences.bp)
    app.register_blueprint(testimonials.bp)
    app.register_blueprint(contact.bp)
    app.register_blueprint(certification.bp)
    app.register_blueprint(generate_token.bp)

    logger.info("Flask application initialization completed successfully", {
        "registered_blueprints": [bp.name for bp in app.blueprints.values()]
    })

    return app
