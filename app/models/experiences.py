from app.models.base import BaseModel
from app.utilities.database import db
from app.models.about import About


class Experiences(BaseModel):
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

    def __repr__(self):
        return f"<Experience {self.designation} at {self.company_name}>"

    def to_dict(self):
        return {
            "Start Year": self.start_year,
            "Address": self.address,
            "Company Name": self.company_name,
            "Description": self.description,
            "Designation": self.designation,
            "End Year": self.end_year,
            "Email": self.email
        }
