from sqlalchemy.sql import func
from app.models.base import BaseModel
from app.utilities.database import db


class About(BaseModel):
    '''
    About DB Structure Model
    '''
    __tablename__ = "about"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    city = db.Column(db.String(100), nullable=False)
    created_date = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    current_company = db.Column(db.String(150), nullable=False)
    current_designation = db.Column(db.String(100), nullable=False)
    degree = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    self_facts = db.Column(db.Text, nullable=False)
    short_description = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    updated_date = db.Column(
        db.DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    website = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<About {self.email}>"

    @classmethod
    def filter_by_email(cls, email):
        """
        Filter records by email.
        :param email: Email to filter by
        :return: The About instance if found, else None.
        """
        return cls.query.filter_by(email=email).first()

    @classmethod
    def fetch_first_record(cls):
        """
        Get the first record from the About table.
        :return: The first About instance if found, else None.
        """
        return cls.query.first()

    @classmethod
    def fetch_first_record_dict(cls):
        """
        Get the first record from the About table as a dictionary.
        :return: Dictionary representation of the first About instance if found, else None.
        """
        first_record = cls.query.first()
        return first_record.to_dict() if first_record else None

    def to_dict(self):
        """
        Convert to a dictionary with UI-friendly Title Case keys.
        """
        return {
            "Email": self.email,
            "City": self.city,
            "Current Company": self.current_company,
            "Current Designation": self.current_designation,
            "Degree": self.degree,
            "Description": self.description,
            "Phone": self.phone,
            "Self Facts": self.self_facts,
            "Short Description": self.short_description,
            "Summary": self.summary,
            "Website": self.website
        }
