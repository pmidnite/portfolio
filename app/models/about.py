from app.utilities.database import db
from sqlalchemy.sql import func


class About(db.Model):
    '''
    About DB Structure Model
    '''
    __tablename__ = "about"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    birthday = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    created_date = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    current_company = db.Column(db.String(150), nullable=False)
    current_designation = db.Column(db.String(100), nullable=False)
    degree = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    phone = db.Column(db.BigInteger, unique=True, nullable=False)
    self_facts = db.Column(db.String(500), nullable=False)
    short_description = db.Column(db.String(500), nullable=False)
    summary = db.Column(db.String(500), nullable=False)
    updated_date = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    website = db.Column(db.String(50), unique=True, nullable=False)
