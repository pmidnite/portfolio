# __init__.py
from flask import Flask
from flask_pymongo import PyMongo
from .config import MONGODB_SETTINGS

app = Flask(__name__)
app.config.update(MONGODB_SETTINGS)

mongo = PyMongo(app)

from app.routes import about, educations, skills, experiences, testimonials, contact

app.register_blueprint(about.bp)
app.register_blueprint(educations.bp)
app.register_blueprint(skills.bp)
app.register_blueprint(experiences.bp)
app.register_blueprint(testimonials.bp)
app.register_blueprint(contact.bp)
