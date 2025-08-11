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

    def __repr__(self):
        return f"<Contact {self.name}>"

    @classmethod
    def filter_by_email(cls, email, all=False, desc=False, asc=False):
        """
        Filter records by email.
        :param email: Email to filter by
        :return: The Contact instance if found, else None.
        """
        if desc:
            return cls.query.filter_by(email=email).order_by(cls.contact_date.desc()).all()
        if asc:
            return cls.query.filter_by(email=email).order_by(cls.contact_date.asc()).all()
        if all:
            return cls.query.filter_by(email=email).all()
        return cls.query.filter_by(email=email).first()

    @classmethod
    def fetch_first_record(cls, email=None):
        """
        Get the first record from the Contact table.
        :param email: Optional email to filter records by
        :return: The first Contact instance if found, else None.
        """
        if email:
            return cls.filter_by_email(email)
        else:
            return cls.query.first()

    @classmethod
    def fetch_first_record_dict(cls, email=None):
        """
        Get the first record from the Contact table as a dictionary.
        :return: Dictionary representation of the first Contact instance if found, else None.
        """
        if email:
            first_record = cls.filter_by_email(email)
        else:
            first_record = cls.query.first()
        return first_record.to_dict() if first_record else None

    @classmethod
    def fetch_all_records(cls, email=None, all=True ,desc=False, asc=False):
        """
        Get all records from the Contact table.
        :param email: Optional email to filter records by
        :param desc: Sort in descending order
        :param asc: Sort in ascending order
        :return: List of Contact instances.
        """
        if email:
            records = cls.filter_by_email(email, all=all, desc=desc, asc=asc)
        else:
            records = cls.query.all()
        return records if records else []

    @classmethod
    def fetch_all_records_dict(cls, email=None, all=True, desc=False, asc=False):
        """
        Get all records from the Contact table as a list of dictionaries.
        :param email: Optional email to filter records by
        :return: List of dictionaries representing Contact instances.
        """
        if email:
            records = cls.filter_by_email(email, all=all, desc=desc, asc=asc)
        else:
            records = cls.query.all()
        return [record.to_dict() for record in records] if records else []

    def save(self):
        """
        Save the contact instance to the database.
        """
        try:
            db.session.add(self)
            db.session.commit()
        except Exception:
            db.session.rollback()

    def delete(self):
        """
        Delete the contact instance from the database.
        """
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception:
            db.session.rollback()

    def to_dict(self):
        return {
            "Name": self.name,
            "Email": self.email,
            "Company": self.company,
            "Designation": self.designation,
            "Message": self.message,
            "Contact Date": self.contact_date.isoformat()  # Convert to ISO format for JSON serialization
        }
