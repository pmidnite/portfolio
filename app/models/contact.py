from app.utilities.database import db
from sqlalchemy.sql import func


class Contact(db.Model):
    '''
    Contact DB Structure Model
    '''
    __tablename__ = "contact"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(150), nullable=False)
    designation = db.Column(db.String(200), nullable=False)
    message = db.Column(db.String(1000), nullable=False)
    contact_date = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
