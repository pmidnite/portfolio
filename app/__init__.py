# __init__.py
from flask import Flask, render_template
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from .config import Config


jwt = JWTManager()
mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    jwt.init_app(app)
    mongo.init_app(app)

    @app.route("/")
    @app.route("/index")
    def index():
        return render_template('index.html')

    from app.routes import about, educations, skills, experiences, testimonials, contact, generate_token

    app.register_blueprint(about.bp)
    app.register_blueprint(educations.bp)
    app.register_blueprint(skills.bp)
    app.register_blueprint(experiences.bp)
    app.register_blueprint(testimonials.bp)
    app.register_blueprint(contact.bp)
    app.register_blueprint(generate_token.bp)

    return app
