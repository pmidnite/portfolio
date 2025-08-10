from app.utilities.database import db


class Certification(db.Model):
    '''
    Certification DB structure Model
    cert_name: Title for the certification(Mandatory)
    cert_logo: Certification image name from the static image certs directory(Mandatory)
    cert_url: Certification public url(Non-Mandatory)
    cert_type: Certification type[Programing Language, Networking, Cybersecurity](Mandatory)
    '''
    __tablename__ = "certification"

    id = db.Column(db.Integer, primary_key=True)
    cert_name = db.Column(db.String(250), unique=True, nullable=False)
    cert_logo = db.Column(db.String(450), nullable=False)
    cert_url = db.Column(db.String(450), nullable=True)
    cert_type = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Certification {self.cert_name}>"

    @classmethod
    def fetch_all_records(cls):
        """
        Get the first record from the Certification table.
        :return: The first Certification instance if found, else None.
        """
        return cls.query.all()

    @classmethod
    def fetch_all_records_dict(cls):
        """
        Get the all record from the Certification table as a dictionary.
        :return: Dictionary representation of the all Certification instance if found, else None.
        """
        all_record = cls.query.all()
        return [record.to_dict() for record in all_record if record]

    @classmethod
    def filter_by_cert_name(cls, cert_name):
        """
        Filter records by cert_name.
        :param cert_name: Cert Name to filter by
        :return: The About instance if found, else None.
        """
        return cls.query.filter_by(cert_name=cert_name).first()

    def save(self):
        """
        Save the current instance to database.
        """
        try:
            db.session.add(self)
            db.session.commit()
        except:
            db.session.rollback()

    def delete(self):
        """
        Delete the current instance from database.
        """
        try:
            db.session.delete(self)
            db.session.commit()
        except:
            db.session.rollback()

    def to_dict(self):
        """
        Convert the Certification instance to a dictionary.
        """
        return {
            "Cert Name": self.cert_name,
            "Cert Logo": self.cert_logo,
            "Cert Url": self.cert_url,
            "Cert Type": self.cert_type
        }
