from app.models.base import BaseModel
from app.utilities.database import db


class Testimonials(BaseModel):
    '''
    Testimony DB Structure Model
    '''
    __tablename__ = "testimony"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    company = db.Column(db.String(150), nullable=True)
    designation = db.Column(db.String(200), nullable=False)
    message = db.Column(db.String(1000), nullable=False)
    reviewed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<Testimonial {self.name}>"

    def to_dict(self):
        return {
            "Name": self.name,
            "Email": self.email,
            "Company": self.company,
            "Designation": self.designation,
            "Message": self.message,
            "Reviewed": self.reviewed
        }
