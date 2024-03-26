from app.utilities.database import db
from sqlalchemy.sql import func
from app.models.about import About


class Experiences(db.Model):
    '''
    Experience DB Structure Model
    '''
    __tablename__ = "experience"

    id = db.Column(db.Integer, primary_key=True)
    start_year = db.Column(db.String(4), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    designation = db.Column(db.String(200), nullable=False)
    end_year = db.Column(db.String(7), nullable=False)
    email = db.Column(db.ForeignKey(About.email), nullable=False)
    
    # __table_args__ = (db.UniqueConstraint(email, start_year, name="email_start_yr_uk"),)
