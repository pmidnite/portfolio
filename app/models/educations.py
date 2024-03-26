from app.utilities.database import db
from sqlalchemy.sql import func
from app.models.about import About


class Education(db.Model):
    '''
    Education DB Structure Model
    '''
    __tablename__ = "education"

    id = db.Column(db.Integer, primary_key=True)
    start_year = db.Column(db.String(4), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    created_date = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    degree = db.Column(db.String(150), nullable=False)
    passing_year = db.Column(db.String(4), nullable=False)
    university = db.Column(db.String(1000), nullable=False)
    updated_date = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    email = db.Column(db.ForeignKey(About.email), nullable=False)
    
    __table_args__ = (db.UniqueConstraint(email, start_year, name="email_start_yr_uk"),)
